import unittest

from parameterized import parameterized
from tests.test_base import TestBase


class TestModulesAndModels(TestBase):

    @parameterized.expand(
        [
            (
                "mps_cli_lanuse_file_per_root",
                "mps.cli.lanuse.library_top",
                "mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_top/mps.cli.lanuse.library_top.msd",
                "mps.cli.lanuse.library_second",
                "mps.cli.lanuse.library_top.authors_top",
                "mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.authors_top/.model",
                "r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed",
            ),
            (
                "mps_cli_lanuse_default_persistency",
                "mps.cli.lanuse.library_top.default_persistency",
                "mps_test_projects/mps_cli_lanuse_default_persistency/solutions/mps.cli.lanuse.library_top.default_persistency",
                "mps.cli.lanuse.library_second.default_persistency",
                "mps.cli.lanuse.library_top.default_persistency.authors_top",
                "mps_test_projects/mps_cli_lanuse_default_persistency/solutions/mps.cli.lanuse.library_top.default_persistency/models/mps.cli.lanuse.library_top.default_persistency.authors_top.mps",
                "r:ca00da79-915e-4bdb-9c30-11a341daf779",
            ),
            (
                # binary models live inside jars and are now read directly from ZIP bytes without extracting to disk. the original approach extracted JARs to a
                # Previously we extracted jar to temp folder which gave each model a real on disk path but
                # the new approach reads bytes in memory so path_to_model_file is not set
                # and so None signals that the path check should be skipped for  this case..
                "mps_cli_lanuse_binary",
                "mps.cli.lanuse.library_top",
                "mps_cli_lanuse_file_per_root",
                "mps.cli.lanuse.library_second",
                "mps.cli.lanuse.library_top.authors_top",
                None,
                "r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed",
            ),
        ]
    )
    def test_build_modules_and_models(
        self,
        test_data_location,
        library_top_solution_name,
        library_top_solution_path,
        library_second_solution_name,
        library_top_authors_top_model_name,
        library_top_authors_top_path,
        library_top_authors_top_model_uuid,
    ):
        """
        Test the building of modules and models
        """
        self.doSetUp(test_data_location)
        self.assertEqual(2, len(self.repo.solutions))

        library_top = self.repo.find_solution_by_name(library_top_solution_name)
        self.assertNotEqual(None, library_top)
        self.assertTrue(
            library_top_solution_path in library_top.path_to_solution_file.as_posix()
        )

        library_second = self.repo.find_solution_by_name(library_second_solution_name)
        self.assertNotEqual(None, library_second)

        library_top_authors_top = self.repo.find_model_by_name(
            library_top_authors_top_model_name
        )
        self.assertNotEqual(None, library_top_authors_top)
        self.assertEqual(
            library_top_authors_top_model_uuid, library_top_authors_top.uuid
        )

        # None means the model came from a jar and has no on disk path to check...
        if library_top_authors_top_path is not None:
            self.assertTrue(
                library_top_authors_top_path
                in library_top_authors_top.path_to_model_file.as_posix()
            )
