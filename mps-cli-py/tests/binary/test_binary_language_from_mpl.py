import sys
import unittest
from pathlib import Path

sys.path.insert(1, "../..")

from mpscli.model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder

# points at the test project folder that contains the jar file jetbrains.mps.build.tips-src.jar
TEST_PROJECT = "../mps_test_projects/mps_cli_binary_persistency_language"


def _build_repo():
    builder = SSolutionsRepositoryBuilder()
    builder.USE_CACHE = False
    return builder.build(str(TEST_PROJECT))


class TestLanguageFromMpl(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo = _build_repo()
        # find the build.tips language specifically
        cls.tips_lang = next(
            (l for l in cls.repo.languages if "build.tips" in l.name),
            None,
        )

    def test_build_tips_language_is_found(self):
        self.assertIsNotNone(
            self.tips_lang,
            "jetbrains.mps.build.tips language should be discovered from the jar",
        )

    def test_language_has_aspect_models_loaded(self):
        self.assertTrue(
            self.tips_lang.models,
            "build.tips language should have aspect models loaded from .mpb files",
        )

    def test_language_uuid_is_set(self):
        uuid = self.tips_lang.uuid
        self.assertIsNotNone(uuid)
        self.assertNotEqual(uuid, "")
        self.assertRegex(
            uuid,
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            f"Language uuidd should be a plain uuid but got: {uuid!r}",
        )
        self.assertEqual(
            "feee615f-9f2b-486f-804f-8987b652fcea",
            uuid,
            "build.tips language UUID does not match the expected value for MPS 2024.1",
        )

    def test_language_version_is_integer(self):
        self.assertIsInstance(self.tips_lang.language_version, int)

    def test_structure_aspect_has_roots(self):
        structure = next(
            (m for m in self.tips_lang.models if "structure" in m.name),
            None,
        )
        self.assertIsNotNone(structure, "structure aspect model should be present")
        self.assertGreater(
            len(structure.root_nodes),
            0,
            "structure aspect should have at least one root node (concept definition)",
        )

    def test_known_concept_present_in_structure(self):
        structure = next(
            (m for m in self.tips_lang.models if "structure" in m.name),
            None,
        )
        self.assertIsNotNone(structure)
        # concept names are stored as the "name" property on ConceptDeclaration root nodes
        concept_names = [r.properties.get("name", "") for r in structure.root_nodes]
        self.assertIn(
            "MPSTipsAndTricks",
            concept_names,
            "MPSTipsAndTricks concept should appear in structure aspect roots",
        )
