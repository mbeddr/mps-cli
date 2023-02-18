import unittest

from parameterized import parameterized
from tests.test_base import TestBase


class TestModulesAndModels(TestBase):

    @parameterized.expand([('mps_cli_lanuse_file_per_root',
                            'mps.cli.lanuse.library_top',
                            'mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_top/mps.cli.lanuse.library_top.msd',
                            'mps.cli.lanuse.library_second',
                            'mps.cli.lanuse.library_top.authors_top',
                            'mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.authors_top/.model',
                            'r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed'),

                           ('mps_cli_lanuse_default_persistency',
                            'mps.cli.lanuse.library_top.default_persistency',
                            'mps_test_projects/mps_cli_lanuse_default_persistency/solutions/mps.cli.lanuse.library_top.default_persistency',
                            'mps.cli.lanuse.library_second.default_persistency',
                            'mps.cli.lanuse.library_top.default_persistency.authors_top',
                            'mps_test_projects/mps_cli_lanuse_default_persistency/solutions/mps.cli.lanuse.library_top.default_persistency/models/mps.cli.lanuse.library_top.default_persistency.authors_top.mps',
                            'r:ca00da79-915e-4bdb-9c30-11a341daf779'),

                           ('mps_cli_lanuse_binary',
                            'mps.cli.lanuse.library_top',
                            'mps_test_projects/mps_cli_lanuse_binary/mps_cli_lanuse_file_per_root_jar/mps.cli.lanuse.library_top',
                            'mps.cli.lanuse.library_second',
                            'mps.cli.lanuse.library_top.authors_top',
                            'mps_test_projects/mps_cli_lanuse_binary/mps_cli_lanuse_file_per_root_jar/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.authors_top/.model',
                            'r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed')])
    def test_build_modules_and_models(self, test_data_location, library_top_solution_name, library_top_solution_path, library_second_solution_name, library_top_authors_top_model_name, library_top_authors_top_path, library_top_authors_top_model_uuid):
        """
        Test the building of modules and models
        """
        self.doSetUp(test_data_location)
        self.assertEqual(2, len(self.repo.solutions))

        library_top = self.repo.find_solution_by_name(library_top_solution_name)
        self.assertNotEqual(None, library_top)
        self.assertTrue(library_top_solution_path in library_top.path_to_solution_file.as_posix())

        library_second = self.repo.find_solution_by_name(library_second_solution_name)
        self.assertNotEqual(None, library_second)

        library_top_authors_top = self.repo.find_model_by_name(library_top_authors_top_model_name)
        self.assertNotEqual(None, library_top_authors_top)
        self.assertEqual(library_top_authors_top_model_uuid, library_top_authors_top.uuid)

        print("---- " + library_top_authors_top.path_to_model_file.as_posix())
        self.assertTrue(library_top_authors_top_path in library_top_authors_top.path_to_model_file.as_posix())

if __name__ == '__main__':
    unittest.main()
