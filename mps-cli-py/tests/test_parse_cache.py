# tests/binary/test_parse_cache.py
#
# Round-trip tests for ParseCache serialization. This verifies that an SModel saved to npz + pkl
# and restored via _restore_model produces a model whose nodes, properties, references
# and parent-child links are identical to the original parsed model

import pickle
import tempfile
import unittest
from pathlib import Path

import numpy as np

from mpscli.model.SModel import SModel
from mpscli.model.builder.SModelBuilderBinaryPersistency import (
    SModelBuilderBinaryPersistency,
)
from mpscli.model.builder.utils.ParseCache import (
    _FileCache,
    _model_meta,
    _model_to_arrays,
    _restore_model,
)

MPB = (
    "../mps_test_projects/"
    "mps_cli_binary_persistency_generated_low_level_access_test_data/"
    "mps.cli.lanuse.library_top.binary_persistency.authors_top.mpb"
)

ROOT_UUID = "4Yb5JA31NUu"
ROOT_CONCEPT = "mps.cli.landefs.people.structure.PersonsContainer"
ROOT_NAME_PROP = "_010_classical_authors"
CHILD_CONCEPT = "mps.cli.landefs.people.structure.Person"
MARK_TWAIN_UUID = "4Yb5JA31NUv"


def _save_and_restore(original_model):
    # serialize original_model to a temp directory using the same format as ParseCache._save_all and then
    # reload with np.load and _restore_model exactly as ParseCache._load_one does on warm runss
    member_name = "test/model.mpb"
    arrays = _model_to_arrays(original_model)
    meta = _model_meta(original_model, member_name)

    with tempfile.TemporaryDirectory() as tmp:
        npz_path = Path(tmp) / "model.npz"
        pkl_path = Path(tmp) / "model_meta.pkl"

        # prefix arrays with m0_ to match the multi-model format used in production
        prefixed = {"m0_" + k: v for k, v in arrays.items()}
        np.savez(str(npz_path), **prefixed)

        with pkl_path.open("wb") as f:
            pickle.dump({"models": [meta]}, f, protocol=pickle.HIGHEST_PROTOCOL)

        # load without mmap so Windows can probably delete the temp file after the test. mmap is basically a
        # read optimization so the correctness of save or restore does not depend on it I think..
        npz = np.load(str(npz_path), allow_pickle=False)
        with pkl_path.open("rb") as f:
            entry = pickle.load(f)

        model_meta_loaded = entry["models"][0]
        model_arrays = {k: npz["m0_" + k] for k in arrays.keys()}
        # explicitly close the NpzFile so Windows releases the file handle before temp directory cleanup..
        # without mmap the arrays are already in memory so closing is safe
        npz.close()

        return _restore_model(model_arrays, model_meta_loaded)


class TestParseCacheRoundTrip(unittest.TestCase):

    def setUp(self):
        builder = SModelBuilderBinaryPersistency()
        self.original = builder.build(MPB)
        self.restored = _save_and_restore(self.original)

    def test_model_name_preserved(self):
        self.assertEqual(self.original.name, self.restored.name)

    def test_model_uuid_preserved(self):
        self.assertEqual(self.original.uuid, self.restored.uuid)

    def test_root_node_count_preserved(self):
        self.assertEqual(
            len(self.original.root_nodes),
            len(self.restored.root_nodes),
        )

    def test_root_uuid_preserved(self):
        self.assertEqual(ROOT_UUID, self.restored.root_nodes[0].uuid)

    def test_root_concept_preserved(self):
        self.assertEqual(ROOT_CONCEPT, self.restored.root_nodes[0].concept.name)

    def test_root_name_property_preserved(self):
        self.assertEqual(
            ROOT_NAME_PROP, self.restored.root_nodes[0].get_property("name")
        )

    def test_all_child_name_properties_preserved(self):
        orig_names = {
            c.get_property("name") for c in self.original.root_nodes[0].children
        }
        rest_names = {
            c.get_property("name") for c in self.restored.root_nodes[0].children
        }
        self.assertEqual(orig_names, rest_names)

    def test_child_count_preserved(self):
        self.assertEqual(
            len(self.original.root_nodes[0].children),
            len(self.restored.root_nodes[0].children),
        )

    def test_all_children_have_correct_concept(self):
        for child in self.restored.root_nodes[0].children:
            self.assertEqual(CHILD_CONCEPT, child.concept.name)

    def test_parent_links_point_to_root(self):
        root = self.restored.root_nodes[0]
        for child in root.children:
            self.assertIs(root, child.parent)

    def test_mark_twain_uuid_preserved(self):
        twain = next(
            (
                c
                for c in self.restored.root_nodes[0].children
                if c.get_property("name") == "Mark Twain"
            ),
            None,
        )
        self.assertIsNotNone(twain, "Mark Twain node not found after restore")
        self.assertEqual(MARK_TWAIN_UUID, twain.uuid)

    def test_role_in_parent_preserved_for_all_children(self):
        orig_roles = [c.role_in_parent for c in self.original.root_nodes[0].children]
        rest_roles = [c.role_in_parent for c in self.restored.root_nodes[0].children]
        self.assertEqual(orig_roles, rest_roles)

    def test_total_node_count_preserved(self):
        self.assertEqual(
            len(self.original.get_nodes()),
            len(self.restored.get_nodes()),
        )

    def test_get_node_by_uuid_finds_root(self):
        found = self.restored.get_node_by_uuid(ROOT_UUID)
        self.assertIs(self.restored.root_nodes[0], found)

    def test_get_node_by_uuid_finds_child(self):
        child = self.restored.root_nodes[0].children[0]
        found = self.restored.get_node_by_uuid(child.uuid)
        self.assertIs(child, found)

    def test_get_node_by_uuid_raises_for_unknown(self):
        with self.assertRaises(KeyError):
            self.restored.get_node_by_uuid("completely_unknown_uuid")

    def test_repeated_root_access_returns_same_object(self):
        # _node_cache must return the same SNode instance on every call
        root_a = self.restored.root_nodes[0]
        root_b = self.restored.get_node_by_uuid(ROOT_UUID)
        self.assertIs(root_a, root_b)

    def test_empty_model_round_trips_without_error(self):
        # verifies the n==0 branch in SModel._finalize() round-trips correctly.. created this inline because
        # setUp builds a non-empty model from the .mpb fixture
        empty = SModel("empty.model", "r:00000000-0000-0000-0000-000000000000", False)
        empty._finalize()
        restored = _save_and_restore(empty)
        self.assertEqual(empty.name, restored.name)
        self.assertEqual(empty.uuid, restored.uuid)
        self.assertEqual(0, len(restored.root_nodes))
        self.assertEqual(0, len(restored.get_nodes()))

    def test_save_all_writes_npz_and_meta_files(self):
        # _save_all should produce one .npz and one _meta.pkl per JAR entry
        to_write = {
            "fake/jar/path.jar": (
                1234567890.0,
                99999,
                {"test/model.mpb": self.original},
            )
        }
        with tempfile.TemporaryDirectory() as tmp:
            cache = _FileCache(Path(tmp), workers=1)
            cache._save_all(to_write)
            files = list(Path(tmp).iterdir())
            npz_files = [f for f in files if f.suffix == ".npz"]
            pkl_files = [f for f in files if f.name.endswith("_meta.pkl")]
            self.assertEqual(len(npz_files), 1)
            self.assertEqual(len(pkl_files), 1)

    def test_save_all_leaves_no_temp_files(self):
        # atomic write should leave no _tmp files behind
        to_write = {
            "fake/jar/path.jar": (
                1234567890.0,
                99999,
                {"test/model.mpb": self.original},
            )
        }
        with tempfile.TemporaryDirectory() as tmp:
            cache = _FileCache(Path(tmp), workers=1)
            cache._save_all(to_write)
            tmp_files = [f for f in Path(tmp).iterdir() if "_tmp" in f.name]
            self.assertEqual(tmp_files, [])

    def test_save_all_bad_entry_does_not_stop_others(self):
        # an exception on one jar entry should not prevent other entries from saving
        good_jar = "fake/good.jar"
        # None key will cause an error when computing md5
        bad_jar = None
        to_write = {
            good_jar: (1234567890.0, 99999, {"model.mpb": self.original}),
            bad_jar: (0.0, 0, {"model.mpb": self.original}),
        }
        import warnings as _warnings

        with tempfile.TemporaryDirectory() as tmp:
            cache = _FileCache(Path(tmp), workers=1)
            with _warnings.catch_warnings(record=True):
                cache._save_all(to_write)
            npz_files = list(Path(tmp).glob("*.npz"))
            self.assertEqual(len(npz_files), 1)

    def test_save_all_empty_dict_completes_without_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = _FileCache(Path(tmp), workers=1)
            cache._save_all({})
            self.assertEqual(list(Path(tmp).iterdir()), [])
