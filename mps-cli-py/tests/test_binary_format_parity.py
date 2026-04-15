import unittest

from tests.test_base import TestBase
from mpscli.model.builder.SSolutionsRepositoryBuilder import (
    SSolutionsRepositoryBuilder,
)

AUTHORS_ROOT_UUID = "4Yb5JA31NUu"


def _repo(location):
    builder = SSolutionsRepositoryBuilder()
    builder.USE_CACHE = False
    return builder.build(f"../mps_test_projects/{location}")


class TestBinaryParityWithOtherFormats(TestBase):
    """
    The binary parser must produce the same logical model as file_per_root
    and default_persistency for the same source content.
    """

    def _authors_root(self, repo, model_name):
        model = repo.find_model_by_name(model_name)
        self.assertIsNotNone(model, f"Model not found: {model_name}")
        self.assertEqual(1, len(model.root_nodes))
        return model.root_nodes[0]

    def _bin_root(self):
        return self._authors_root(
            _repo("mps_cli_binary_persistency_generated"),
            "mps.cli.lanuse.library_top.binary_persistency.authors_top",
        )

    def test_root_uuid_matches_file_per_root(self):
        fpr = self._authors_root(
            _repo("mps_cli_lanuse_file_per_root"),
            "mps.cli.lanuse.library_top.authors_top",
        )
        self.assertEqual(AUTHORS_ROOT_UUID, fpr.uuid)
        self.assertEqual(fpr.uuid, self._bin_root().uuid)

    def test_root_concept_matches_file_per_root(self):
        fpr = self._authors_root(
            _repo("mps_cli_lanuse_file_per_root"),
            "mps.cli.lanuse.library_top.authors_top",
        )
        self.assertEqual(fpr.concept.name, self._bin_root().concept.name)

    def test_person_count_matches_file_per_root(self):
        fpr = self._authors_root(
            _repo("mps_cli_lanuse_file_per_root"),
            "mps.cli.lanuse.library_top.authors_top",
        )
        self.assertEqual(len(fpr.children), len(self._bin_root().children))

    def test_person_names_match_file_per_root(self):
        fpr = self._authors_root(
            _repo("mps_cli_lanuse_file_per_root"),
            "mps.cli.lanuse.library_top.authors_top",
        )
        fpr_names = sorted(c.get_property("name") for c in fpr.children)
        bin_names = sorted(c.get_property("name") for c in self._bin_root().children)
        self.assertEqual(fpr_names, bin_names)

    def test_root_uuid_matches_default_persistency(self):
        dp = self._authors_root(
            _repo("mps_cli_lanuse_default_persistency"),
            "mps.cli.lanuse.library_top.default_persistency.authors_top",
        )
        self.assertEqual(AUTHORS_ROOT_UUID, dp.uuid)
