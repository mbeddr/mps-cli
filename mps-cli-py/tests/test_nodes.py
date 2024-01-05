import unittest

from tests.test_base import TestBase
from parameterized import parameterized


class TestNodes(TestBase):

    @parameterized.expand([('mps_cli_lanuse_file_per_root',
                            'mps.cli.lanuse.library_top.authors_top'),
                           ('mps_cli_lanuse_default_persistency',
                            'mps.cli.lanuse.library_top.default_persistency.authors_top'),
                           ('mps_cli_lanuse_binary',
                            'mps.cli.lanuse.library_top.authors_top')])
    def test_build_root_nodes(self, test_data_location, library_top_authors_top_model_name):
        """
        Test the building of root nodes
        """
        self.doSetUp(test_data_location)

        library_top_authors_top = self.repo.find_model_by_name(library_top_authors_top_model_name)

        self.assertEqual(1, len(library_top_authors_top.root_nodes))
        root_node = library_top_authors_top.root_nodes[0]
        self.assertEqual('4Yb5JA31NUu', root_node.uuid)
        self.assertEqual("mps.cli.landefs.people.structure.PersonsContainer", root_node.concept.name)
        self.assertEqual("_010_classical_authors", root_node.properties["name"])

    @parameterized.expand([('mps_cli_lanuse_file_per_root',
                            'mps.cli.lanuse.library_top.library_top'),
                           ('mps_cli_lanuse_default_persistency',
                            'mps.cli.lanuse.library_top.default_persistency.library_top'),
                           ('mps_cli_lanuse_binary',
                            'mps.cli.lanuse.library_top.library_top')])
    def test_build_nodes(self, test_data_location, library_top_library_top_model_name):
        """
        Test the building of nodes
        """
        self.doSetUp(test_data_location)
        library_top_library_top = self.repo.find_model_by_name(library_top_library_top_model_name)

        root_nodes=library_top_library_top.root_nodes
        root_nodes.sort(key=get_name)
        root_node = root_nodes[0]
        self.assertEqual("munich_library", root_node.get_property("name"))

        tom_sawyer = root_node.get_children("entities")[0]
        self.assertEqual("Tom Sawyer", tom_sawyer.get_property("name"))
        author_of_tom_sawyer = tom_sawyer.get_children("authors")[0].get_reference("person").resolve(self.repo)
        self.assertEqual("Mark Twain", author_of_tom_sawyer.get_property("name"))

def get_name(node):
    return node.get_property("name")

if __name__ == '__main__':
    unittest.main()