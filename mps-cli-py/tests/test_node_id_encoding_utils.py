import unittest

from mpscli.model.builder.utils.NodeIdEncodingUtils import NodeIdEncodingUtils


class TestNodeIdEncodingUtils(unittest.TestCase):

    def setUp(self):
        self.utils = NodeIdEncodingUtils()

    def test_decode(self):
        self.assertEqual("5731700211660045983", self.utils.decode("4Yb5JA31NUv"))

    def test_encode(self):
        self.assertEqual("4Yb5JA31NUv", self.utils.encode("5731700211660045983"))

    def test_round_trip(self):
        original = "5731700211660045983"
        encoded = self.utils.encode(original)
        decoded = self.utils.decode(encoded)

        self.assertEqual(original, decoded)
