# tests/test_jar_scanner.py
#
# Tests for JarScanner - the phase1 ZIP central directory scanner.

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from mpscli.model.builder.utils.JarScanner import scan_jar, scan_all_jars, JarScanResult

# test projects that have jars with known content
_BINARY_PROJECT = os.path.abspath(
    "../mps_test_projects/mps_cli_binary_persistency_generated"
)
_BINARY_JAR_DIR = Path(_BINARY_PROJECT)


def _find_jars(path: Path):
    return list(path.rglob("*.jar"))


class TestScanJar(unittest.TestCase):

    def setUp(self):
        self._jars = _find_jars(_BINARY_JAR_DIR)
        self.assertTrue(len(self._jars) > 0, "no JARs found in test project")

    def test_scan_jar_returns_result_for_relevant_jar(self):
        # at least one har in the binary test project should be relevant
        results = [scan_jar(jp) for jp in self._jars]
        non_none = [r for r in results if r is not None]
        self.assertTrue(len(non_none) > 0)

    def test_scan_jar_result_has_solution_infos(self):
        results = [r for r in (scan_jar(jp) for jp in self._jars) if r is not None]
        all_solutions = [si for r in results for si in r.solution_infos]
        self.assertTrue(len(all_solutions) > 0)

    def test_scan_jar_result_has_mpb_members(self):
        results = [r for r in (scan_jar(jp) for jp in self._jars) if r is not None]
        all_mpb = [m for r in results for m in r.all_mpb_members]
        self.assertTrue(len(all_mpb) > 0)

    def test_scan_jar_solution_has_name_and_uuid(self):
        results = [r for r in (scan_jar(jp) for jp in self._jars) if r is not None]
        for r in results:
            for si in r.solution_infos:
                self.assertTrue(len(si.solution.name) > 0)
                self.assertTrue(len(si.solution.uuid) > 0)

    def test_scan_jar_populates_jar_stats(self):
        results = [r for r in (scan_jar(jp) for jp in self._jars) if r is not None]
        for r in results:
            for jar_str, (mtime, size) in r.jar_stats.items():
                self.assertIsInstance(mtime, float)
                self.assertGreater(size, 0)

    def test_scan_jar_mpb_members_reference_correct_jar(self):
        for jp in self._jars:
            result = scan_jar(jp)
            if result is None:
                continue
            for jar_str, member_name in result.all_mpb_members:
                self.assertEqual(jar_str, str(jp))
                self.assertTrue(member_name.endswith(".mpb"))

    def test_scan_jar_no_duplicate_mpb_members(self):
        for jp in self._jars:
            result = scan_jar(jp)
            if result is None:
                continue
            seen = set()
            for pair in result.all_mpb_members:
                self.assertNotIn(pair, seen, f"duplicate mpb member: {pair}")
                seen.add(pair)

    def test_scan_nonexistent_jar_returns_none(self):
        result = scan_jar(Path("/nonexistent/path/fake.jar"))
        self.assertIsNone(result)

    def test_scan_jar_language_infos_have_namespace(self):
        results = [r for r in (scan_jar(jp) for jp in self._jars) if r is not None]
        for r in results:
            for namespace, uuid, version, members in r.language_infos:
                self.assertTrue(len(namespace) > 0)
                self.assertIsInstance(version, int)


class TestScanAllJars(unittest.TestCase):

    def setUp(self):
        self._jars = _find_jars(_BINARY_JAR_DIR)
        self.assertTrue(len(self._jars) > 0, "no JARs found in test project")

    def test_scan_all_jars_returns_combined_result(self):
        result = scan_all_jars(self._jars, workers=4)
        self.assertIsInstance(result, JarScanResult)
        self.assertTrue(len(result.solution_infos) > 0)

    def test_scan_all_jars_no_duplicate_mpb_members(self):
        result = scan_all_jars(self._jars, workers=4)
        seen = set()
        for pair in result.all_mpb_members:
            self.assertNotIn(pair, seen, f"duplicate mpb member: {pair}")
            seen.add(pair)

    def test_scan_all_jars_collects_jar_stats(self):
        result = scan_all_jars(self._jars, workers=4)
        self.assertTrue(len(result.jar_stats) > 0)

    def test_scan_all_jars_empty_list_returns_empty_result(self):
        result = scan_all_jars([], workers=4)
        self.assertEqual(result.solution_infos, [])
        self.assertEqual(result.all_mpb_members, [])
        self.assertEqual(result.language_infos, [])

    def test_scan_all_jars_workers_1_matches_workers_4(self):
        # result should be equivalent regardless of the thread count..
        r1 = scan_all_jars(self._jars, workers=1)
        r4 = scan_all_jars(self._jars, workers=4)
        self.assertEqual(len(r1.solution_infos), len(r4.solution_infos))
        self.assertEqual(
            sorted(str(j) + m for j, m in r1.all_mpb_members),
            sorted(str(j) + m for j, m in r4.all_mpb_members),
        )
