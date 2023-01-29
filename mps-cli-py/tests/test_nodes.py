import unittest
import os

from model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder
from tests.test_base import TestBase


class TestModulesAndModels(TestBase):

    def test_build_root_nodes(self):
        """
        Test the building of root nodes
        """
        library_top_authors_top = self.repo.find_model_by_name('mps.cli.lanuse.library_top.authors_top')

        self.assertEqual(1, len(library_top_authors_top.root_nodes))
        root_node = library_top_authors_top.root_nodes[0]
        self.assertEqual("4Yb5JA31NUu", root_node.uuid)
        self.assertEqual("mps.cli.landefs.people.structure.PersonsContainer", root_node.concept.name)
        self.assertEqual("_010_classical_authors", root_node.properties["name"])

    def test_build_nodes(self):
        """
        Test the building of nodes
        """
        library_top_library_top = self.repo.find_model_by_name('mps.cli.lanuse.library_top.library_top')

        root_node = library_top_library_top.root_nodes[0]
        self.assertEqual("munich_library", root_node.get_property("name"))

        tom_sawyer = root_node.get_children("entities")[0]
        self.assertEqual("Tom Sawyer", tom_sawyer.get_property("name"))
        author_of_tom_sawyer = tom_sawyer.get_children("authors")[0].get_reference("person").resolve(self.repo)
        self.assertEqual("Mark Twain", author_of_tom_sawyer.get_property("name"))


if __name__ == '__main__':
    unittest.main()