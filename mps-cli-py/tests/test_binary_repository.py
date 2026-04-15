import unittest

from mpscli.model.builder.SSolutionsRepositoryBuilder import (
    SSolutionsRepositoryBuilder,
)

REPO_PATH = "../mps_test_projects/mps_cli_binary_persistency_generated/"
SOLUTION_NAME = "mps.cli.lanuse.library_top.binary_persistency"
LIB_MODEL_NAME = "mps.cli.lanuse.library_top.binary_persistency.library_top"
AUTH_MODEL_NAME = "mps.cli.lanuse.library_top.binary_persistency.authors_top"


def _build_repo():
    builder = SSolutionsRepositoryBuilder()
    builder.USE_CACHE = False
    return builder.build(REPO_PATH)


class TestBinaryRepository(unittest.TestCase):
    def setUp(self):
        self.repo = _build_repo()

    def test_library_top_solution_exists(self):
        self.assertIsNotNone(self.repo.find_solution_by_name(SOLUTION_NAME))

    def test_library_top_solution_has_two_models(self):
        sol = self.repo.find_solution_by_name(SOLUTION_NAME)
        self.assertEqual(2, len(sol.models))

    def test_library_top_model_found(self):
        self.assertIsNotNone(self.repo.find_model_by_name(LIB_MODEL_NAME))

    def test_authors_top_model_found(self):
        self.assertIsNotNone(self.repo.find_model_by_name(AUTH_MODEL_NAME))

    def test_no_placeholder_uuids(self):
        for sol in self.repo.solutions:
            for model in sol.models:
                self.assertRegex(
                    model.uuid,
                    r"^r:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                    f"Model UUID {model.uuid!r} is a placeholdder or not in 'r:uuid' format",
                )

    def test_library_language_present(self):
        self.assertIsNotNone(self.repo.find_language_by_name("mps.cli.landefs.library"))

    def test_people_language_present(self):
        self.assertIsNotNone(self.repo.find_language_by_name("mps.cli.landefs.people"))

    def test_lang_core_present(self):
        self.assertIsNotNone(self.repo.find_language_by_name("jetbrains.mps.lang.core"))
