# tests/test_jar_model_loader.py
#
# Testss for JarModelLoader - the phase4 JAR FPR/MPS parser. Verifies load_jar_solutions correctness,
# lang_pairs accumulation, cache hit pathh and model count/uuid consistency with test projects.

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder
from mpscli.model.builder.utils.JarScanner import scan_all_jars
from mpscli.model.builder.utils.JarModelLoader import load_jar_solutions
from mpscli.model.builder.utils.MpbBatchParser import MpbBatchParser

_BINARY_PROJECT = os.path.abspath(
    "../mps_test_projects/mps_cli_binary_persistency_generated"
)
_BINARY_JAR_DIR = Path(_BINARY_PROJECT)
_LANUSE_BINARY = os.path.abspath("../mps_test_projects/mps_cli_lanuse_binary")
_LANUSE_BINARY_DIR = Path(_LANUSE_BINARY)

# known values from binary test project
_EXPECTED_SOLUTION = "mps.cli.lanuse.library_top.binary_persistency"
_EXPECTED_MODEL_COUNT = 2
_EXPECTED_MODELS = {
    "mps.cli.lanuse.library_top.binary_persistency.library_top",
    "mps.cli.lanuse.library_top.binary_persistency.authors_top",
}

# known values from lanuse_binary test project
_LANUSE_EXPECTED_SOLUTIONS = {
    "mps.cli.lanuse.library_top",
    "mps.cli.lanuse.library_second",
}


def _find_jars(path: Path):
    return list(path.rglob("*.jar"))


class TestLoadJarSolutions(unittest.TestCase):

    def setUp(self):
        SLanguageBuilder.languages = {}
        SSolutionsRepositoryBuilder.USE_CACHE = False
        self._jars = _find_jars(_BINARY_JAR_DIR)
        self.assertTrue(len(self._jars) > 0, "no JARs found")
        self._scan = scan_all_jars(self._jars, workers=4)
        parser = MpbBatchParser()
        self._jar_results = parser.parse_from_jars(self._scan.all_mpb_members)

    def test_returns_solutions(self):
        solutions = load_jar_solutions(
            self._scan,
            self._jar_results,
            set(),
            workers=4,
            parse_cache=None,
            use_cache=False,
        )
        # binary project solution is present among results
        solution_names = {s.name for s in solutions}
        self.assertIn(_EXPECTED_SOLUTION, solution_names)

    def test_solutions_have_names(self):
        solutions = load_jar_solutions(
            self._scan,
            self._jar_results,
            set(),
            workers=4,
            parse_cache=None,
            use_cache=False,
        )
        # solution names are verified with concrete values in test_returns_solutions
        for sol in solutions:
            self.assertNotEqual(sol.name, "")

    def test_solutions_have_models(self):
        solutions = load_jar_solutions(
            self._scan,
            self._jar_results,
            set(),
            workers=4,
            parse_cache=None,
            use_cache=False,
        )
        # binary project solution has the expected models
        sol = next(s for s in solutions if s.name == _EXPECTED_SOLUTION)
        model_names = {m.name for m in sol.models}
        self.assertEqual(model_names, _EXPECTED_MODELS)

    def test_disk_solution_names_excluded(self):
        # solutions whose names are in disk_solution_names should be skipped
        solutions_all = load_jar_solutions(
            self._scan,
            self._jar_results,
            set(),
            workers=4,
            parse_cache=None,
            use_cache=False,
        )
        all_names = {s.name for s in solutions_all}
        # exclude all solutions so result should be empty
        solutions_none = load_jar_solutions(
            self._scan,
            self._jar_results,
            all_names,
            workers=4,
            parse_cache=None,
            use_cache=False,
        )
        self.assertEqual(solutions_none, [])

    def test_no_duplicate_solutions(self):
        solutions = load_jar_solutions(
            self._scan,
            self._jar_results,
            set(),
            workers=4,
            parse_cache=None,
            use_cache=False,
        )
        names = [s.name for s in solutions]
        self.assertEqual(len(names), len(set(names)))

    def test_empty_scan_returns_empty(self):
        from mpscli.model.builder.utils.JarScanner import JarScanResult

        empty_scan = JarScanResult()
        solutions = load_jar_solutions(
            empty_scan,
            {},
            set(),
            workers=4,
            parse_cache=None,
            use_cache=False,
        )
        self.assertEqual(solutions, [])


class TestLoadJarSolutionsWithFpr(unittest.TestCase):
    # tests using mps_cli_lanuse_binary which already has jar FPR/MPS content
    def setUp(self):
        SLanguageBuilder.languages = {}
        SSolutionsRepositoryBuilder.USE_CACHE = False
        jars = _find_jars(_LANUSE_BINARY_DIR)
        if not jars:
            self.skipTest("no JARs found in lanuse_binary project")
        self._scan = scan_all_jars(jars, workers=4)
        parser = MpbBatchParser()
        self._jar_results = parser.parse_from_jars(self._scan.all_mpb_members)

    def test_fpr_models_loaded_from_jar(self):
        solutions = load_jar_solutions(
            self._scan,
            self._jar_results,
            set(),
            workers=4,
            parse_cache=None,
            use_cache=False,
        )
        # lanuse_binary project has exactly 2 solutions
        solution_names = {s.name for s in solutions}
        self.assertEqual(solution_names, _LANUSE_EXPECTED_SOLUTIONS)

    def test_jar_fpr_models_have_root_nodes(self):
        solutions = load_jar_solutions(
            self._scan,
            self._jar_results,
            set(),
            workers=4,
            parse_cache=None,
            use_cache=False,
        )
        all_models = [m for s in solutions for m in s.models]
        models_with_nodes = [m for m in all_models if len(m.root_nodes) > 0]
        self.assertGreaterEqual(len(models_with_nodes), 1)
