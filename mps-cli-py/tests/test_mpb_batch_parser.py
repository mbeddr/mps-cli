# tests/test_mpb_batch_parser.py
#
# Tests for MpbBatchParser - the phase2 binary model parser. Covers parse_from_jars serial/parallel threshold,
# lang_pairs registration and concept registration in the main process for small batches and result completeness..

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.utils.JarScanner import scan_all_jars
from mpscli.model.builder.utils.MpbBatchParser import (
    MpbBatchParser,
    _register_lang_pairs,
)

_BINARY_PROJECT = os.path.abspath(
    "../mps_test_projects/mps_cli_binary_persistency_generated"
)
_BINARY_JAR_DIR = Path(_BINARY_PROJECT)

# known values from the binary test project
_EXPECTED_MPB_COUNT = 13
_EXPECTED_LANGUAGES = {
    "mps.cli.landefs.library",
    "mps.cli.landefs.people",
    "jetbrains.mps.lang.core",
}


def _find_jars(path: Path):
    return list(path.rglob("*.jar"))


class TestRegisterLangPairs(unittest.TestCase):

    def setUp(self):
        SLanguageBuilder.languages = {}

    def test_register_lang_pairs_adds_languages(self):
        _register_lang_pairs([("my.lang", "uuid-001"), ("other.lang", "uuid-002")])
        self.assertIn("my.lang", SLanguageBuilder.languages)
        self.assertIn("other.lang", SLanguageBuilder.languages)

    def test_register_lang_pairs_idempotent(self):
        _register_lang_pairs([("my.lang", "uuid-001")])
        _register_lang_pairs([("my.lang", "uuid-001")])
        self.assertEqual(len(SLanguageBuilder.languages), 1)

    def test_register_lang_pairs_empty_list_does_not_raise(self):
        _register_lang_pairs([])
        self.assertEqual(SLanguageBuilder.languages, {})


class TestMpbBatchParserParseFromJars(unittest.TestCase):

    def setUp(self):
        SLanguageBuilder.languages = {}
        self._jars = _find_jars(_BINARY_JAR_DIR)
        self.assertTrue(len(self._jars) > 0, "no JARs found in test project")
        self._scan = scan_all_jars(self._jars, workers=4)

    def test_parse_from_jars_returns_all_members(self):
        parser = MpbBatchParser()
        results = parser.parse_from_jars(self._scan.all_mpb_members)
        # binary project has exactly 13 mpb members
        self.assertEqual(len(results), _EXPECTED_MPB_COUNT)

    def test_parse_from_jars_no_none_models(self):
        parser = MpbBatchParser()
        results = parser.parse_from_jars(self._scan.all_mpb_members)
        for key, model in results.items():
            self.assertIsNotNone(model, f"model is None for {key}")

    def test_parse_from_jars_registers_languages_in_main_process(self):
        # small project has less than PARALLEL_THRESHOLD unique JARs so serial path is used
        # concepts must be registered in the main process so SLanguageBuilder is populated
        SLanguageBuilder.languages = {}
        parser = MpbBatchParser()
        parser.parse_from_jars(self._scan.all_mpb_members)
        registered = set(SLanguageBuilder.languages.keys())
        for lang in _EXPECTED_LANGUAGES:
            self.assertIn(lang, registered)

    def test_parse_from_jars_empty_returns_empty_dict(self):
        parser = MpbBatchParser()
        results = parser.parse_from_jars([])
        self.assertEqual(results, {})

    def test_parse_from_jars_models_have_uuid(self):
        parser = MpbBatchParser()
        results = parser.parse_from_jars(self._scan.all_mpb_members)
        for key, model in results.items():
            self.assertNotEqual(model.uuid, "", f"model uuid empty for {key}")

    def test_parse_from_jars_models_have_name(self):
        parser = MpbBatchParser()
        results = parser.parse_from_jars(self._scan.all_mpb_members)
        for key, model in results.items():
            self.assertNotEqual(model.name, "", f"model name empty for {key}")

    def test_parallel_threshold_default_is_5(self):
        self.assertEqual(MpbBatchParser.PARALLEL_THRESHOLD, 5)

    def test_parse_from_jars_result_keys_match_input(self):
        parser = MpbBatchParser()
        members = self._scan.all_mpb_members
        results = parser.parse_from_jars(members)
        for jar_str, member_name in members:
            self.assertIn((jar_str, member_name), results)


class TestMpbBatchParserParse(unittest.TestCase):

    def setUp(self):
        SLanguageBuilder.languages = {}

    def test_parse_empty_list_returns_empty_dict(self):
        parser = MpbBatchParser()
        self.assertEqual(parser.parse([]), {})

    def test_parse_single_mpb_file(self):
        mpb = os.path.abspath(
            "../mps_test_projects/"
            "mps_cli_binary_persistency_generated_low_level_access_test_data/"
            "mps.cli.lanuse.library_top.binary_persistency.authors_top.mpb"
        )
        if not os.path.exists(mpb):
            self.skipTest("test mpb file not found")
        parser = MpbBatchParser()
        results = parser.parse([mpb])
        self.assertIn(mpb, results)
        self.assertIsNotNone(results[mpb])

    def test_parse_nonexistent_path_returns_none_not_exception(self):
        parser = MpbBatchParser()
        import warnings

        with warnings.catch_warnings(record=True):
            results = parser.parse(["/nonexistent/fake.mpb"])
        self.assertIn("/nonexistent/fake.mpb", results)
        self.assertIsNone(results["/nonexistent/fake.mpb"])
