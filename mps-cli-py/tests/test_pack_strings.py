# tests/binary/test_pack_strings.py
#
# Unit tests for pack_strings in FlatModelPacker.

import unittest

from mpscli.model.builder.utils.FlatModelPacker import pack_strings


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


class TestPackStrings(unittest.TestCase):

    def test_empty_list_produces_single_zero_offset_and_empty_bytes(self):
        offsets, data = pack_strings([])
        self.assertEqual(len(offsets), 1)
        self.assertEqual(int(offsets[0]), 0)
        self.assertEqual(data, b"")

    def test_single_string_round_trips(self):
        offsets, data = pack_strings(["hello"])
        self.assertEqual(_decode_string(data, offsets, 0), "hello")

    def test_multiple_strings_all_round_trip(self):
        strings = ["alpha", "beta", "gamma"]
        offsets, data = pack_strings(strings)
        for i, s in enumerate(strings):
            self.assertEqual(_decode_string(data, offsets, i), s)

    def test_empty_string_in_middle_round_trips(self):
        offsets, data = pack_strings(["before", "", "after"])
        self.assertEqual(_decode_string(data, offsets, 0), "before")
        self.assertEqual(_decode_string(data, offsets, 1), "")
        self.assertEqual(_decode_string(data, offsets, 2), "after")

    def test_all_empty_strings(self):
        offsets, data = pack_strings(["", "", ""])
        self.assertEqual(data, b"")
        for i in range(3):
            self.assertEqual(_decode_string(data, offsets, i), "")

    def test_multibyte_utf8_character_round_trips(self):
        # euro sign is 3 bytes in UTF-8 and thiss verifies that byte-length is used not char-length
        strings = ["price: 5\u20ac", "normal"]
        offsets, data = pack_strings(strings)
        self.assertEqual(_decode_string(data, offsets, 0), "price: 5\u20ac")
        self.assertEqual(_decode_string(data, offsets, 1), "normal")
