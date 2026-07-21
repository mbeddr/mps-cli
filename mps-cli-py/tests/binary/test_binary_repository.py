import tempfile
import unittest
from pathlib import Path

from mpscli.model.builder.SSolutionsRepositoryBuilder import (
    SSolutionsRepositoryBuilder,
)
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.utils.ParseCache import ParseCache, _FileCache

REPO_PATH = "../mps_test_projects/mps_cli_binary_persistency_generated/"
SOLUTION_NAME = "mps.cli.lanuse.library_top.binary_persistency"
LIB_MODEL_NAME = "mps.cli.lanuse.library_top.binary_persistency.library_top"
AUTH_MODEL_NAME = "mps.cli.lanuse.library_top.binary_persistency.authors_top"


def _build_repo():
    SLanguageBuilder.languages = {}
    SSolutionsRepositoryBuilder.USE_CACHE = False
    return SSolutionsRepositoryBuilder().build(REPO_PATH)


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


class TestBinaryRepositoryWithCacheEnabled(unittest.TestCase):
    # verifies that USE_CACHE=True (the default) produces the same correct results
    # as USE_CACHE=False for the binary persistency test project..

    def setUp(self):
        SLanguageBuilder.languages = {}
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cache_root = Path(self._tmp.name)
        original_init = ParseCache.__init__

        def patched_init(self_pc, workers=None):
            w = workers or 4
            self_pc._xml = _FileCache(cache_root / "jar_xml", w)
            self_pc._disk = _FileCache(cache_root / "disk_solutions", w)

        ParseCache.__init__ = patched_init
        self._original_init = original_init
        SSolutionsRepositoryBuilder.USE_CACHE = True
        self.repo = SSolutionsRepositoryBuilder().build(REPO_PATH)

    def tearDown(self):
        ParseCache.__init__ = self._original_init
        SSolutionsRepositoryBuilder.USE_CACHE = False
        self._tmp.cleanup()

    def test_cache_enabled_solution_exists(self):
        self.assertIsNotNone(self.repo.find_solution_by_name(SOLUTION_NAME))

    def test_cache_enabled_solution_has_two_models(self):
        sol = self.repo.find_solution_by_name(SOLUTION_NAME)
        self.assertEqual(2, len(sol.models))

    def test_cache_enabled_languages_present(self):
        self.assertIsNotNone(self.repo.find_language_by_name("mps.cli.landefs.library"))
        self.assertIsNotNone(self.repo.find_language_by_name("jetbrains.mps.lang.core"))
