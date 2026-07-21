# tests/test_solutions_repository_builder.py
#
# Tests for SSolutionsRepositoryBuilder. This covers the enhanced build() API where individual JAR file paths, 
# mixed directory + jar lists and jar_filter regex scenarios.

import os
import unittest
from pathlib import Path

from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder

_BINARY_PROJECT = os.path.abspath(
    "../mps_test_projects/mps_cli_binary_persistency_generated"
)
_BINARY_JAR_DIR = Path(_BINARY_PROJECT)

# known jar filenames in the binary test project
_JAR_LIBRARY_TOP = str(
    _BINARY_JAR_DIR / "mps.cli.lanuse.library_top.binary_persistency-src.jar"
)
_JAR_LIBRARY_SECOND = str(
    _BINARY_JAR_DIR / "mps.cli.lanuse.library_second.binary_persistency-src.jar"
)
_JAR_LANDEFS_LIBRARY = str(_BINARY_JAR_DIR / "mps.cli.landefs.library-src.jar")

_SOLUTION_LIBRARY_TOP = "mps.cli.lanuse.library_top.binary_persistency"
_SOLUTION_LIBRARY_SECOND = "mps.cli.lanuse.library_second.binary_persistency"


def _reset():
    SLanguageBuilder.languages = {}
    SSolutionsRepositoryBuilder.USE_CACHE = False


class TestBuildWithDirectory(unittest.TestCase):
    # baseline is existing directory path behaviour still works correctly
    def setUp(self):
        _reset()

    def test_directory_path_parses_all_jars(self):
        repo = SSolutionsRepositoryBuilder().build(_BINARY_PROJECT)
        solution_names = {s.name for s in repo.solutions}
        self.assertIn(_SOLUTION_LIBRARY_TOP, solution_names)
        self.assertIn(_SOLUTION_LIBRARY_SECOND, solution_names)

    def test_nonexistent_path_warns_and_returns_empty(self):
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            repo = SSolutionsRepositoryBuilder().build("/nonexistent/path")
        self.assertEqual(len(repo.solutions), 0)
        self.assertTrue(
            any("not found" in str(warning.message).lower() for warning in w)
        )


class TestBuildWithIndividualJar(unittest.TestCase):

    def setUp(self):
        _reset()

    def test_single_jar_path_parses_only_that_jar(self):
        repo = SSolutionsRepositoryBuilder().build(_JAR_LIBRARY_TOP)
        solution_names = {s.name for s in repo.solutions}
        # only library_top solution should be present and library_second jar was not passed
        self.assertIn(_SOLUTION_LIBRARY_TOP, solution_names)
        self.assertNotIn(_SOLUTION_LIBRARY_SECOND, solution_names)

    def test_two_jar_paths_parse_both(self):
        repo = SSolutionsRepositoryBuilder().build(
            [_JAR_LIBRARY_TOP, _JAR_LIBRARY_SECOND]
        )
        solution_names = {s.name for s in repo.solutions}
        self.assertIn(_SOLUTION_LIBRARY_TOP, solution_names)
        self.assertIn(_SOLUTION_LIBRARY_SECOND, solution_names)

    def test_jar_path_produces_correct_model_count(self):
        repo = SSolutionsRepositoryBuilder().build(_JAR_LIBRARY_TOP)
        sol = repo.find_solution_by_name(_SOLUTION_LIBRARY_TOP)
        self.assertIsNotNone(sol)
        self.assertEqual(len(sol.models), 2)

    def test_nonexistent_jar_warns_and_returns_empty(self):
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            repo = SSolutionsRepositoryBuilder().build("/nonexistent/fake.jar")
        self.assertEqual(len(repo.solutions), 0)
        self.assertTrue(
            any("not found" in str(warning.message).lower() for warning in w)
        )

    def test_non_jar_file_logs_error_and_skips(self):
        # a file that exists but is not a .jar should be skipped with an error log
        msd_file = str(next(_BINARY_JAR_DIR.rglob("*.jar")).parent / "nonexistent.txt")
        repo = SSolutionsRepositoryBuilder().build([msd_file, _JAR_LIBRARY_TOP])
        # library_top should still be parsedd even though the non jar was skipped
        self.assertIsNotNone(repo.find_solution_by_name(_SOLUTION_LIBRARY_TOP))


class TestBuildMixedDirectoryAndJar(unittest.TestCase):

    def setUp(self):
        _reset()

    def test_mixed_list_directory_and_jar(self):
        # pass directory which contains all jars and a specific jar but no duplicates
        repo = SSolutionsRepositoryBuilder().build([_BINARY_PROJECT, _JAR_LIBRARY_TOP])
        solution_names = {s.name for s in repo.solutions}
        self.assertIn(_SOLUTION_LIBRARY_TOP, solution_names)
        self.assertIn(_SOLUTION_LIBRARY_SECOND, solution_names)
        # no duplicate solutions
        names = [s.name for s in repo.solutions]
        self.assertEqual(len(names), len(set(names)))


class TestBuildWithJarFilter(unittest.TestCase):

    def setUp(self):
        _reset()

    def test_jar_filter_includes_matching_jars(self):
        # filter to only library_top jar by filename pattern
        repo = SSolutionsRepositoryBuilder().build(
            _BINARY_PROJECT, jar_filter=r"library_top"
        )
        solution_names = {s.name for s in repo.solutions}
        self.assertIn(_SOLUTION_LIBRARY_TOP, solution_names)

    def test_jar_filter_excludes_non_matching_jars(self):
        # filter to only library_top and library_second should not be parsed
        repo = SSolutionsRepositoryBuilder().build(
            _BINARY_PROJECT, jar_filter=r"library_top"
        )
        solution_names = {s.name for s in repo.solutions}
        self.assertNotIn(_SOLUTION_LIBRARY_SECOND, solution_names)

    def test_jar_filter_no_match_returns_empty(self):
        repo = SSolutionsRepositoryBuilder().build(
            _BINARY_PROJECT, jar_filter=r"this_pattern_matches_nothing_xyz"
        )
        self.assertEqual(len(repo.solutions), 0)

    def test_individual_jar_bypasses_jar_filter(self):
        # explicitly named jar should always be included regardless of jar_filter
        repo = SSolutionsRepositoryBuilder().build(
            [_BINARY_PROJECT, _JAR_LIBRARY_SECOND], jar_filter=r"library_top"
        )
        solution_names = {s.name for s in repo.solutions}
        # library_top matches filter from directory scan
        self.assertIn(_SOLUTION_LIBRARY_TOP, solution_names)
        # library_second was explicitly passed so it bypasses the filter
        self.assertIn(_SOLUTION_LIBRARY_SECOND, solution_names)

    def test_jar_filter_with_regex_pattern(self):
        # test a proper regex pattern tat matches jars starting with mps.cli.lanuse
        repo = SSolutionsRepositoryBuilder().build(
            _BINARY_PROJECT, jar_filter=r"mps\.cli\.lanuse\."
        )
        solution_names = {s.name for s in repo.solutions}
        # both lanuse solutions should be present
        self.assertIn(_SOLUTION_LIBRARY_TOP, solution_names)
        self.assertIn(_SOLUTION_LIBRARY_SECOND, solution_names)
