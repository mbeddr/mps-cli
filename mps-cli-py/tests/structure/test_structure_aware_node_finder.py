import unittest

from mpscli.model.structure.StructureAwareSNodeClassFinder import StructureAwareSNodeClassFinder


class TestStructureAwareNodeFinder(unittest.TestCase):

    def test_find_concepts(self):
        # given + when we have an initialized finder
        finder = StructureAwareSNodeClassFinder(".")

        # then expect to find 9 node classes
        self.assertEqual(7, len(finder.concept_name_2_snode_class))


if __name__ == '__main__':
    unittest.main()
