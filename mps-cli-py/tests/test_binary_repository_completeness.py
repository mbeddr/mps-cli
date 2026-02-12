from tests.test_base import TestBase
from mpscli.model.builder.SSolutionsRepositoryBuilder import (
    SSolutionsRepositoryBuilder,
)


class TestBinaryRepositoryCompleteness(TestBase):

    REPO_PATH = "../mps_test_projects/" "mps_cli_binary_persistency_generated/"

    def test_build_repository(self):
        builder = SSolutionsRepositoryBuilder()
        repo = builder.build(self.REPO_PATH)

        self.assertIsNotNone(repo)
        self.assertGreater(len(repo.solutions), 0)

    def test_solution_and_model_structure(self):
        builder = SSolutionsRepositoryBuilder()
        repo = builder.build(self.REPO_PATH)

        library_solution = repo.find_solution_by_name(
            "mps.cli.lanuse.library_top.binary_persistency"
        )

        self.assertIsNotNone(library_solution)
        self.assertEqual(len(library_solution.models), 2)

        model = repo.find_model_by_name(
            "mps.cli.lanuse.library_top.binary_persistency.library_top"
        )

        self.assertIsNotNone(model)
        self.assertGreater(len(model.root_nodes), 0)

    def test_root_node_properties_and_descendants(self):
        builder = SSolutionsRepositoryBuilder()
        repo = builder.build(self.REPO_PATH)

        model = repo.find_model_by_name(
            "mps.cli.lanuse.library_top.binary_persistency.library_top"
        )

        root = next(
            r for r in model.root_nodes if r.get_property("name") == "munich_library"
        )

        self.assertIsNotNone(root)

        descendants = model.get_nodes()
        self.assertGreater(len(descendants), 0)

        entities = root.get_children("entities")
        self.assertEqual(len(entities), 4)

    def test_cross_model_reference_resolution(self):
        builder = SSolutionsRepositoryBuilder()
        repo = builder.build(self.REPO_PATH)

        model = repo.find_model_by_name(
            "mps.cli.lanuse.library_top.binary_persistency.library_top"
        )

        root = next(
            r for r in model.root_nodes if r.get_property("name") == "munich_library"
        )

        book = root.get_children("entities")[0]
        authors = book.get_children("authors")

        reference = authors[0].get_reference("person")

        self.assertIsNotNone(reference)
        self.assertTrue(reference.model_uuid.startswith("r:"))
        self.assertIsNotNone(reference.node_uuid)

        resolved = reference.resolve(repo)
        self.assertIsNotNone(resolved)

    def test_language_registry_population(self):
        builder = SSolutionsRepositoryBuilder()
        repo = builder.build(self.REPO_PATH)

        languages = repo.languages

        self.assertGreaterEqual(len(languages), 3)

        names = [l.name for l in languages]

        self.assertIn("mps.cli.landefs.library", names)
        self.assertIn("mps.cli.landefs.people", names)
        self.assertIn("jetbrains.mps.lang.core", names)
