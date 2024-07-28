import unittest

from mpscli.model.builder.NodeIdEncodingUtils import NodeIdEncodingUtils


class TestStringUtils(unittest.TestCase):

    def test_string_utils(self):
        """
        Test the StringUtils
        """
        su = NodeIdEncodingUtils()
        self.assertEqual(5731700211660045982, su.decode_string('4Yb5JA31NUu'))

if __name__ == '__main__':
    unittest.main()