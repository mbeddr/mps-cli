import unittest

from mpscli.model.builder.SSolutionsRepositoryBuilder import (
    SSolutionsRepositoryBuilder,
)

REPO_PATH = "../mps_test_projects/mps_cli_binary_persistency_generated/"
LIB_MODEL_NAME = "mps.cli.lanuse.library_top.binary_persistency.library_top"


def _build_repo():
    builder = SSolutionsRepositoryBuilder()
    builder.USE_CACHE = False
    return builder.build(REPO_PATH)


class TestLibraryTopModel(unittest.TestCase):
    def setUp(self):
        repo = _build_repo()
        self.model = repo.find_model_by_name(LIB_MODEL_NAME)
        self.assertIsNotNone(self.model)
        self.munich = next(
            (
                r
                for r in self.model.root_nodes
                if r.get_property("name") == "munich_library"
            ),
            None,
        )

    def test_has_two_root_nodes(self):
        self.assertEqual(2, len(self.model.root_nodes))

    def test_total_node_count(self):
        self.assertEqual(9, len(self.model.get_nodes()))

    def test_munich_library_root_exists(self):
        self.assertIsNotNone(self.munich)

    def test_munich_library_descendants_count(self):
        self.assertEqual(7, len(self.munich.get_descendants()))

    def test_entities_count(self):
        self.assertEqual(4, len(self.munich.get_children("entities")))

    def test_first_book_name(self):
        book = self.munich.get_children("entities")[0]
        self.assertEqual("Tom Sawyer", book.get_property("name"))

    def test_first_book_publication_date(self):
        book = self.munich.get_children("entities")[0]
        self.assertEqual("1876", book.get_property("publicationDate"))

    def test_first_book_isbn(self):
        book = self.munich.get_children("entities")[0]
        self.assertEqual("4323r2", book.get_property("isbn"))

    def test_first_book_available(self):
        book = self.munich.get_children("entities")[0]
        self.assertEqual("true", book.get_property("available"))

    def test_first_book_concept(self):
        book = self.munich.get_children("entities")[0]
        self.assertEqual("mps.cli.landefs.library.structure.Book", book.concept.name)

    def test_first_book_role_in_parent(self):
        book = self.munich.get_children("entities")[0]
        self.assertEqual("entities", book.role_in_parent)

    def test_first_book_has_authors(self):
        book = self.munich.get_children("entities")[0]
        self.assertGreater(len(book.get_children("authors")), 0)

    def test_all_entities_have_name(self):
        for entity in self.munich.get_children("entities"):
            self.assertIsNotNone(entity.get_property("name"))
            self.assertGreater(len(entity.get_property("name")), 0)

    def test_parent_links_throughout_tree(self):
        for root in self.model.root_nodes:
            self.assertIsNone(root.parent)
            for child in root.children:
                self.assertIs(root, child.parent)
                for grandchild in child.children:
                    self.assertIs(child, grandchild.parent)


if __name__ == "__main__":
    unittest.main()
