import unittest

from parameterized import parameterized
from tests.test_base import TestBase
from mpscli.model.builder.SSolutionsRepositoryBuilder import (
    SSolutionsRepositoryBuilder,
)

MARK_TWAIN_NODE_UUID = "4Yb5JA31NUv"
MARK_TWAIN_RESOLVE_INFO = "Mark Twain"
MARK_TWAIN_CONCEPT = "mps.cli.landefs.people.structure.Person"


def _build_repo(repo_path):
    builder = SSolutionsRepositoryBuilder()
    builder.USE_CACHE = False
    return builder.build(repo_path)


def _get_mark_twain_ref(repo, lib_model_name):
    lib = repo.find_model_by_name(lib_model_name)
    munich = next(
        r for r in lib.root_nodes if r.get_property("name") == "munich_library"
    )
    book = munich.get_children("entities")[0]
    authors = book.get_children("authors")
    return authors[0].get_reference("person"), lib


class TestCrossModelReferenceResolution(TestBase):
    @parameterized.expand(
        [
            (
                "mps_cli_binary_persistency_generated",
                "mps.cli.lanuse.library_top.binary_persistency.library_top",
            ),
        ]
    )
    def test_resolve_info_is_mark_twain(self, test_data_location, lib_model_name):
        self.doSetUp(test_data_location)
        ref, _ = _get_mark_twain_ref(self.repo, lib_model_name)
        self.assertEqual(MARK_TWAIN_RESOLVE_INFO, ref.resolve_info)

    @parameterized.expand(
        [
            (
                "mps_cli_binary_persistency_generated",
                "mps.cli.lanuse.library_top.binary_persistency.library_top",
            ),
        ]
    )
    def test_node_uuid_is_mark_twain(self, test_data_location, lib_model_name):
        self.doSetUp(test_data_location)
        ref, _ = _get_mark_twain_ref(self.repo, lib_model_name)
        self.assertEqual(MARK_TWAIN_NODE_UUID, ref.node_uuid)

    @parameterized.expand(
        [
            (
                "mps_cli_binary_persistency_generated",
                "mps.cli.lanuse.library_top.binary_persistency.library_top",
            ),
        ]
    )
    def test_model_uuid_format(self, test_data_location, lib_model_name):
        self.doSetUp(test_data_location)
        ref, _ = _get_mark_twain_ref(self.repo, lib_model_name)
        self.assertRegex(
            ref.model_uuid,
            r"^r:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            f"Reference model_uuid {ref.model_uuid!r} not in expected 'r:uuid' format",
        )

    @parameterized.expand(
        [
            (
                "mps_cli_binary_persistency_generated",
                "mps.cli.lanuse.library_top.binary_persistency.library_top",
            ),
        ]
    )
    def test_resolved_node_concept(self, test_data_location, lib_model_name):
        self.doSetUp(test_data_location)
        ref, _ = _get_mark_twain_ref(self.repo, lib_model_name)
        resolved = ref.resolve(self.repo)
        self.assertEqual(MARK_TWAIN_CONCEPT, resolved.concept.name)

    @parameterized.expand(
        [
            (
                "mps_cli_binary_persistency_generated",
                "mps.cli.lanuse.library_top.binary_persistency.library_top",
            ),
        ]
    )
    def test_resolved_node_uuid_matches(self, test_data_location, lib_model_name):
        self.doSetUp(test_data_location)
        ref, _ = _get_mark_twain_ref(self.repo, lib_model_name)
        resolved = ref.resolve(self.repo)
        self.assertEqual(MARK_TWAIN_NODE_UUID, resolved.uuid)

    @parameterized.expand(
        [
            (
                "mps_cli_binary_persistency_generated",
                "mps.cli.lanuse.library_top.binary_persistency.library_top",
            ),
        ]
    )
    def test_all_lib_references_have_r_uuid(self, test_data_location, lib_model_name):
        self.doSetUp(test_data_location)
        _, lib = _get_mark_twain_ref(self.repo, lib_model_name)
        for node in lib.get_nodes():
            for ref in node.references.values():
                self.assertTrue(
                    ref.model_uuid.startswith("r:"),
                    f"Reference model_uuid {ref.model_uuid!r} not in r: format",
                )
