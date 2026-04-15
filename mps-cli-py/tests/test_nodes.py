import unittest

from tests.test_base import TestBase
from parameterized import parameterized


class TestNodes(TestBase):

    @parameterized.expand(
        [
            ("mps_cli_lanuse_file_per_root", "mps.cli.lanuse.library_top.authors_top"),
            (
                "mps_cli_lanuse_default_persistency",
                "mps.cli.lanuse.library_top.default_persistency.authors_top",
            ),
            ("mps_cli_lanuse_binary", "mps.cli.lanuse.library_top.authors_top"),
            (
                "mps_cli_binary_persistency_generated",
                "mps.cli.lanuse.library_top.binary_persistency.authors_top",
            ),
        ]
    )
    def test_build_root_nodes(
        self, test_data_location, library_top_authors_top_model_name
    ):
        self.doSetUp(test_data_location)

        library_top_authors_top = self.repo.find_model_by_name(
            library_top_authors_top_model_name
        )

        self.assertEqual(1, len(library_top_authors_top.root_nodes))
        root_node = library_top_authors_top.root_nodes[0]
        self.assertEqual("4Yb5JA31NUu", root_node.uuid)
        self.assertEqual(
            "mps.cli.landefs.people.structure.PersonsContainer", root_node.concept.name
        )
        self.assertEqual("_010_classical_authors", root_node.properties["name"])
        self.assertEqual(None, root_node.parent)

    @parameterized.expand(
        [
            ("mps_cli_lanuse_file_per_root", "mps.cli.lanuse.library_top.library_top"),
            (
                "mps_cli_lanuse_default_persistency",
                "mps.cli.lanuse.library_top.default_persistency.library_top",
            ),
            ("mps_cli_lanuse_binary", "mps.cli.lanuse.library_top.library_top"),
            (
                "mps_cli_binary_persistency_generated",
                "mps.cli.lanuse.library_top.binary_persistency.library_top",
            ),
        ]
    )
    def test_build_nodes(self, test_data_location, library_top_library_top_model_name):
        self.doSetUp(test_data_location)
        library_top_library_top = self.repo.find_model_by_name(
            library_top_library_top_model_name
        )

        root_nodes = library_top_library_top.root_nodes
        root_nodes.sort(key=get_name)
        root_node = root_nodes[0]
        self.assertEqual("munich_library", root_node.get_property("name"))

        tom_sawyer = root_node.get_children("entities")[0]
        self.assertEqual("Tom Sawyer", tom_sawyer.get_property("name"))
        author_of_tom_sawyer = (
            tom_sawyer.get_children("authors")[0]
            .get_reference("person")
            .resolve(self.repo)
        )
        self.assertEqual("Mark Twain", author_of_tom_sawyer.get_property("name"))
        self.assertEqual(root_node, tom_sawyer.parent)

    @parameterized.expand(
        [
            ("mps_cli_lanuse_file_per_root", "mps.cli.lanuse.library_top.library_top"),
            (
                "mps_cli_lanuse_default_persistency",
                "mps.cli.lanuse.library_top.default_persistency.library_top",
            ),
            ("mps_cli_lanuse_binary", "mps.cli.lanuse.library_top.library_top"),
            (
                "mps_cli_binary_persistency_generated",
                "mps.cli.lanuse.library_top.binary_persistency.library_top",
            ),
        ]
    )
    def test_library_top_model_completeness(
        self, test_data_location, library_top_library_top_model_name
    ):
        self.doSetUp(test_data_location)
        model = self.repo.find_model_by_name(library_top_library_top_model_name)
        self.assertIsNotNone(model)

        self.assertEqual(2, len(model.root_nodes))
        self.assertEqual(9, len(model.get_nodes()))

        root = next(
            r for r in model.root_nodes if r.get_property("name") == "munich_library"
        )
        self.assertIsNotNone(root)
        self.assertEqual(7, len(root.get_descendants()))

        entities = root.get_children("entities")
        self.assertEqual(4, len(entities))

        book = entities[0]
        self.assertEqual("Tom Sawyer", book.get_property("name"))
        self.assertEqual("1876", book.get_property("publicationDate"))
        self.assertEqual("4323r2", book.get_property("isbn"))
        self.assertEqual("true", book.get_property("available"))
        self.assertEqual(
            "mps.cli.landefs.library.structure.Book",
            book.concept.name,
        )
        self.assertEqual("entities", book.role_in_parent)

        authors = book.get_children("authors")
        self.assertEqual(1, len(authors))

        reference = authors[0].get_reference("person")
        self.assertIsNotNone(reference)
        self.assertRegex(
            reference.model_uuid,
            r"^r:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            f"Reference model_uuid {reference.model_uuid!r} not in expected 'r:uuid' format",
        )

        resolved = reference.resolve(self.repo)
        self.assertIsNotNone(resolved)
        self.assertEqual("Mark Twain", resolved.get_property("name"))

    def test_library_top_model_completeness_binary_reference_details(self):
        self.doSetUp("mps_cli_binary_persistency_generated")
        model = self.repo.find_model_by_name(
            "mps.cli.lanuse.library_top.binary_persistency.library_top"
        )
        root = next(
            r for r in model.root_nodes if r.get_property("name") == "munich_library"
        )
        book = root.get_children("entities")[0]
        reference = book.get_children("authors")[0].get_reference("person")
        self.assertEqual("Mark Twain", reference.resolve_info)
        self.assertEqual("4Yb5JA31NUv", reference.node_uuid)


def get_name(node):
    return node.get_property("name")
