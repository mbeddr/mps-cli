# tests/test_disk_model_loader.py
#
# Tests for DiskModelLoader - the phase3 disk FPR/MPS parser. Verifies load_disk_solutions correctness, 
# preread_disk_bytes, warm cache path, lang_pairs accumulation and model count consistency withh test projects.

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.utils.DiskModelLoader import (
    load_disk_solutions,
    preread_disk_bytes,
    parse_fpr,
    parse_mps,
    _collect_model_paths,
)

_FPR_PROJECT = os.path.abspath("../mps_test_projects/mps_cli_lanuse_file_per_root")
_MPS_PROJECT = os.path.abspath(
    "../mps_test_projects/mps_cli_lanuse_default_persistency"
)
_BINARY_PROJECT = os.path.abspath(
    "../mps_test_projects/mps_cli_binary_persistency_generated"
)


def _msd_paths(project_dir):
    return sorted(Path(project_dir).rglob("*.msd"))


class TestLoadDiskSolutionsFpr(unittest.TestCase):

    def setUp(self):
        SLanguageBuilder.languages = {}
        self._msd_paths = _msd_paths(_FPR_PROJECT)
        self.assertTrue(len(self._msd_paths) > 0, "no msd files found")

    def test_returns_solutions(self):
        solutions = load_disk_solutions(self._msd_paths)
        self.assertTrue(len(solutions) > 0)

    def test_solutions_have_names(self):
        solutions = load_disk_solutions(self._msd_paths)
        for sol in solutions:
            self.assertTrue(len(sol.name) > 0)

    def test_solutions_have_models(self):
        solutions = load_disk_solutions(self._msd_paths)
        total_models = sum(len(s.models) for s in solutions)
        self.assertGreater(total_models, 0)

    def test_models_have_root_nodes(self):
        solutions = load_disk_solutions(self._msd_paths)
        all_models = [m for s in solutions for m in s.models]
        # at least some models should have root nodes
        models_with_nodes = [m for m in all_models if len(m.root_nodes) > 0]
        self.assertTrue(len(models_with_nodes) > 0)

    def test_models_have_uuid(self):
        solutions = load_disk_solutions(self._msd_paths)
        for sol in solutions:
            for model in sol.models:
                self.assertTrue(len(model.uuid) > 0)

    def test_registers_languages(self):
        SLanguageBuilder.languages = {}
        load_disk_solutions(self._msd_paths)
        self.assertTrue(len(SLanguageBuilder.languages) > 0)


class TestLoadDiskSolutionsMps(unittest.TestCase):

    def setUp(self):
        SLanguageBuilder.languages = {}
        self._msd_paths = _msd_paths(_MPS_PROJECT)
        self.assertTrue(len(self._msd_paths) > 0, "no msd files found")

    def test_returns_solutions_for_mps_project(self):
        solutions = load_disk_solutions(self._msd_paths)
        self.assertTrue(len(solutions) > 0)

    def test_mps_solutions_have_models(self):
        solutions = load_disk_solutions(self._msd_paths)
        total_models = sum(len(s.models) for s in solutions)
        self.assertGreater(total_models, 0)


class TestLoadDiskSolutionsEdgeCases(unittest.TestCase):

    def setUp(self):
        SLanguageBuilder.languages = {}

    def test_empty_msd_list_returns_empty(self):
        solutions = load_disk_solutions([])
        self.assertEqual(solutions, [])

    def test_preread_bytes_used_when_provided(self):
        msd_paths = _msd_paths(_FPR_PROJECT)
        if not msd_paths:
            self.skipTest("no msd files")
        preread = preread_disk_bytes(msd_paths)
        # preread should have populated some entries
        self.assertTrue(len(preread) > 0)
        # using preread should produce same result as not using it
        SLanguageBuilder.languages = {}
        sols_with = load_disk_solutions(msd_paths, preread_bytes=preread)
        SLanguageBuilder.languages = {}
        sols_without = load_disk_solutions(msd_paths, preread_bytes=None)
        self.assertEqual(
            sum(len(s.models) for s in sols_with),
            sum(len(s.models) for s in sols_without),
        )


class TestPrereadDiskBytes(unittest.TestCase):

    def setUp(self):
        SLanguageBuilder.languages = {}

    def test_preread_returns_bytes_for_fpr_project(self):
        msd_paths = _msd_paths(_FPR_PROJECT)
        if not msd_paths:
            self.skipTest("no msd files")
        preread = preread_disk_bytes(msd_paths)
        fpr_keys = [k for k in preread if k[0] == "fpr"]
        self.assertTrue(len(fpr_keys) > 0)

    def test_preread_fpr_value_is_bytes_and_list(self):
        msd_paths = _msd_paths(_FPR_PROJECT)
        if not msd_paths:
            self.skipTest("no msd files")
        preread = preread_disk_bytes(msd_paths)
        for key, value in preread.items():
            if key[0] == "fpr":
                model_bytes, mpsr_data = value
                self.assertIsInstance(model_bytes, bytes)
                self.assertIsInstance(mpsr_data, list)
                break

    def test_preread_empty_msd_list_returns_empty(self):
        preread = preread_disk_bytes([])
        self.assertEqual(preread, {})


class TestParseFprAndMps(unittest.TestCase):

    def setUp(self):
        SLanguageBuilder.languages = {}

    def test_parse_fpr_returns_model(self):
        # find a real FPR directory in the test project
        for msd in _msd_paths(_FPR_PROJECT):
            models_dir = msd.parent / "models"
            if not models_dir.exists():
                continue
            _, fpr_dirs, _ = _collect_model_paths(models_dir)
            if fpr_dirs:
                model = parse_fpr(fpr_dirs[0])
                self.assertIsNotNone(model)
                self.assertTrue(len(model.name) > 0)
                return
        self.skipTest("no FPR directories found")

    def test_parse_mps_returns_model(self):
        # find a real .mps file in the default persistency test project
        for msd in _msd_paths(_MPS_PROJECT):
            models_dir = msd.parent / "models"
            if not models_dir.exists():
                continue
            _, _, mps_files = _collect_model_paths(models_dir)
            if mps_files:
                model = parse_mps(mps_files[0])
                self.assertIsNotNone(model)
                self.assertTrue(len(model.name) > 0)
                return
        self.skipTest("no MPS files found")


class TestCollectModelPaths(unittest.TestCase):

    def test_collect_finds_fpr_dirs(self):
        for msd in _msd_paths(_FPR_PROJECT):
            models_dir = msd.parent / "models"
            if not models_dir.exists():
                continue
            mpb, fpr, mps = _collect_model_paths(models_dir)
            self.assertTrue(len(fpr) > 0)
            return
        self.skipTest("no models directory found")

    def test_fpr_dirs_have_dot_model_file(self):
        for msd in _msd_paths(_FPR_PROJECT):
            models_dir = msd.parent / "models"
            if not models_dir.exists():
                continue
            _, fpr, _ = _collect_model_paths(models_dir)
            for fp in fpr:
                self.assertTrue((fp / ".model").exists())
            return
        self.skipTest("no models directory found")

    def test_collect_finds_mps_files(self):
        for msd in _msd_paths(_MPS_PROJECT):
            models_dir = msd.parent / "models"
            if not models_dir.exists():
                continue
            _, _, mps = _collect_model_paths(models_dir)
            self.assertTrue(len(mps) > 0)
            return
        self.skipTest("no models directory found")
