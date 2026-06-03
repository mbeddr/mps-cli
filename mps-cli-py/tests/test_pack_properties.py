# tests/binary/test_pack_properties.py
#
# Unit tests for pack_properties in FlatModelPacker.

import unittest

from mpscli.model.builder.utils.FlatModelPacker import pack_properties


def _decode_string(data, offsets, idx):
    # helper that mirrors SModel._read_bytes and is used to verify round-trips
    start = int(offsets[idx])
    end = int(offsets[idx + 1])
    if start == end:
        return ""
    chunk = data[start:end]
    if hasattr(chunk, "tobytes"):
        return chunk.tobytes().decode()
    return chunk.decode()


def _get_props(result, node_idx):
    # reconstruct the property dict for a given node
    prop_start, prop_key_idxs, prop_val_offsets, prop_val_data, prop_keys = result
    start = int(prop_start[node_idx])
    end = int(prop_start[node_idx + 1])
    result_dict = {}
    for j in range(start, end):
        key = prop_keys[int(prop_key_idxs[j])]
        val = _decode_string(prop_val_data, prop_val_offsets, j)
        result_dict[key] = val
    return result_dict


class TestPackProperties(unittest.TestCase):

    def test_all_empty_dicts_produce_zero_properties(self):
        prop_start, key_idxs, _, _, prop_keys = pack_properties([{}, {}, {}])
        self.assertEqual(len(prop_keys), 0)
        self.assertEqual(len(key_idxs), 0)
        for i in range(3):
            self.assertEqual(int(prop_start[i]), int(prop_start[i + 1]))

    def test_empty_properties_list(self):
        prop_start, _, _, _, _ = pack_properties([])
        self.assertEqual(len(prop_start), 1)
        self.assertEqual(int(prop_start[0]), 0)

    def test_single_node_with_properties_round_trips(self):
        properties = [{"name": "Alice", "age": "30"}]
        result = pack_properties(properties)
        props = _get_props(result, 0)
        self.assertEqual(props["name"], "Alice")
        self.assertEqual(props["age"], "30")

    def test_multiple_nodes_with_varying_property_counts(self):
        properties = [
            {"name": "Mark Twain"},
            {},
            {"name": "Hemingway", "year": "1899"},
        ]
        result = pack_properties(properties)
        self.assertEqual(_get_props(result, 0), {"name": "Mark Twain"})
        self.assertEqual(_get_props(result, 1), {})
        self.assertEqual(_get_props(result, 2), {"name": "Hemingway", "year": "1899"})

    def test_repeated_key_is_deduplicated_in_prop_keys(self):
        # 'name' appears on all three nodes but should only appear once in prop_keys
        properties = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        _, _, _, _, prop_keys = pack_properties(properties)
        self.assertEqual(prop_keys.count("name"), 1)

    def test_none_value_stored_as_empty_string(self):
        properties = [{"description": None}]
        result = pack_properties(properties)
        props = _get_props(result, 0)
        self.assertEqual(props["description"], "")
