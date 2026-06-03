# tests/binary/test_pack_references.py
#
# Unit tests for pack_references in FlatModelPacker.

import unittest

from mpscli.model.builder.utils.FlatModelPacker import pack_references


def _decode_string(data, offsets, idx):
    # helper that mirrors SModel._read_bytes - used to verify round-trips
    start = int(offsets[idx])
    end = int(offsets[idx + 1])
    if start == end:
        return ""
    chunk = data[start:end]
    if hasattr(chunk, "tobytes"):
        return chunk.tobytes().decode()
    return chunk.decode()


class _FakeRef:
    def __init__(self, model_uuid, node_uuid, resolve_info):
        self.model_uuid = model_uuid
        self.node_uuid = node_uuid
        self.resolve_info = resolve_info


def _get_ref(result, node_idx, role):
    # reconstruct one reference for a given node and role
    (
        ref_start,
        ref_key_idxs,
        ref_model_idxs,
        ref_node_uuid_offsets,
        ref_node_uuid_data,
        ref_resolve_offsets,
        ref_resolve_data,
        ref_keys,
        ref_model_uuids,
    ) = result
    start = int(ref_start[node_idx])
    end = int(ref_start[node_idx + 1])
    key_idx = ref_keys.index(role) if role in ref_keys else -1
    for j in range(start, end):
        if int(ref_key_idxs[j]) == key_idx:
            model_uuid = ref_model_uuids[int(ref_model_idxs[j])]
            node_uuid = _decode_string(ref_node_uuid_data, ref_node_uuid_offsets, j)
            resolve = _decode_string(ref_resolve_data, ref_resolve_offsets, j)
            return model_uuid, node_uuid, resolve
    return None


class TestPackReferences(unittest.TestCase):

    def test_all_empty_dicts_produce_zero_references(self):
        result = pack_references([{}, {}, {}])
        ref_start, ref_key_idxs = result[0], result[1]
        self.assertEqual(len(ref_key_idxs), 0)
        for i in range(3):
            self.assertEqual(int(ref_start[i]), int(ref_start[i + 1]))

    def test_empty_references_list(self):
        result = pack_references([])
        self.assertEqual(len(result[0]), 1)
        self.assertEqual(int(result[0][0]), 0)

    def test_single_node_with_reference_round_trips(self):
        ref = _FakeRef("r:model-uuid-123", "node-uuid-456", "MyType")
        result = pack_references([{"extends": ref}])
        found = _get_ref(result, 0, "extends")
        self.assertIsNotNone(found)
        model_uuid, node_uuid, resolve = found
        self.assertEqual(model_uuid, "r:model-uuid-123")
        self.assertEqual(node_uuid, "node-uuid-456")
        self.assertEqual(resolve, "MyType")

    def test_model_uuid_is_deduplicated_in_ref_model_uuids(self):
        # same model_uuid on two different nodes should appear once only
        ref_a = _FakeRef("r:shared-model", "node-1", "TypeA")
        ref_b = _FakeRef("r:shared-model", "node-2", "TypeB")
        result = pack_references([{"role1": ref_a}, {"role2": ref_b}])
        self.assertEqual(result[8].count("r:shared-model"), 1)

    def test_role_names_are_deduplicated_in_ref_keys(self):
        ref_a = _FakeRef("r:m1", "n1", "T1")
        ref_b = _FakeRef("r:m2", "n2", "T2")
        result = pack_references([{"type": ref_a}, {"type": ref_b}])
        self.assertEqual(result[7].count("type"), 1)

    def test_node_with_no_references_has_empty_slice(self):
        ref = _FakeRef("r:m", "n", "T")
        result = pack_references([{}, {"role": ref}, {}])
        ref_start = result[0]
        self.assertEqual(int(ref_start[0]), int(ref_start[1]))
        self.assertEqual(int(ref_start[2]) - int(ref_start[1]), 1)
        self.assertEqual(int(ref_start[2]), int(ref_start[3]))

    def test_none_model_uuid_stored_as_empty_string(self):
        ref = _FakeRef(None, "node-uuid", "SomeType")
        result = pack_references([{"ref": ref}])
        self.assertIn("", result[8])
