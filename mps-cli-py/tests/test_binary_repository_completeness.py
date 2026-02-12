from tests.test_base import TestBase
from mpscli.model.builder.SSolutionsRepositoryBuilder import (
    SSolutionsRepositoryBuilder,
)


class TestBinaryRepositoryCompleteness(TestBase):

    REPO_PATH = "../mps_test_projects/" "mps_cli_binary_persistency_generated/"

    def _build_repo(self):
        builder = SSolutionsRepositoryBuilder()
        return builder.build(self.REPO_PATH)

    def test_repository_builds(self):
        repo = self._build_repo()

        self.assertIsNotNone(repo)
        self.assertGreater(len(repo.solutions), 0)

    def test_library_top_model_completeness(self):
        repo = self._build_repo()

        solution = repo.find_solution_by_name(
            "mps.cli.lanuse.library_top.binary_persistency"
        )
        self.assertIsNotNone(solution)
        self.assertEqual(len(solution.models), 2)

        model = repo.find_model_by_name(
            "mps.cli.lanuse.library_top.binary_persistency.library_top"
        )
        self.assertIsNotNone(model)

        self.assertEqual(len(model.root_nodes), 2)

        self.assertEqual(len(model.get_nodes()), 9)

        root = next(
            r for r in model.root_nodes if r.get_property("name") == "munich_library"
        )

        self.assertIsNotNone(root)

        self.assertEqual(len(root.get_descendants()), 7)

        entities = root.get_children("entities")
        self.assertEqual(len(entities), 4)

        book = entities[0]
        self.assertEqual(book.get_property("name"), "Tom Sawyer")
        self.assertEqual(book.get_property("publicationDate"), "1876")
        self.assertEqual(book.get_property("isbn"), "4323r2")
        self.assertEqual(book.get_property("available"), "true")

        self.assertEqual(
            book.concept.name,
            "mps.cli.landefs.library.structure.Book",
        )

        self.assertEqual(book.role_in_parent, "entities")

        authors = book.get_children("authors")
        self.assertGreater(len(authors), 0)

        reference = authors[0].get_reference("person")

        self.assertIsNotNone(reference)
        self.assertEqual(reference.resolve_info, "Mark Twain")
        self.assertTrue(reference.model_uuid.startswith("r:"))
        self.assertEqual(reference.node_uuid, "4Yb5JA31NUv")

        resolved = reference.resolve(repo)
        self.assertIsNotNone(resolved)

    def test_language_registry_population(self):
        repo = self._build_repo()

        languages = repo.languages
        self.assertGreaterEqual(len(languages), 3)

        names = [l.name for l in languages]

        self.assertIn("mps.cli.landefs.library", names)
        self.assertIn("mps.cli.landefs.people", names)
        self.assertIn("jetbrains.mps.lang.core", names)
