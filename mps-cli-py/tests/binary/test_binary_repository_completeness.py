from tests.test_base import TestBase
from mpscli.model.builder.SSolutionsRepositoryBuilder import (
    SSolutionsRepositoryBuilder,
)


class TestBinaryRepositoryCompleteness(TestBase):
    REPO_PATH = "../mps_test_projects/mps_cli_binary_persistency_generated/"

    def _build_repo(self):
        builder = SSolutionsRepositoryBuilder()
        builder.USE_CACHE = False
        return builder.build(self.REPO_PATH)

    def test_repository_builds(self):
        repo = self._build_repo()
        self.assertIsNotNone(repo)
        self.assertIsNotNone(
            repo.find_solution_by_name("mps.cli.lanuse.library_top.binary_persistency"),
            "Expected mps.cli.lanuse.library_top.binary_persistency solution to be present",
        )

    def test_language_registry_population(self):
        repo = self._build_repo()

        languages = repo.languages
        self.assertGreaterEqual(len(languages), 3)

        names = [l.name for l in languages]
        self.assertIn("mps.cli.landefs.library", names)
        self.assertIn("mps.cli.landefs.people", names)
        self.assertIn("jetbrains.mps.lang.core", names)
