import unittest

from parameterized import parameterized
from tests.test_base import TestBase


class TestModulesAndModels(TestBase):

    @parameterized.expand([('mps_cli_lanuse_file_per_root',
                            'mps.cli.lanuse.library_top',
                            'mps.cli.lanuse.library_second',
                            'mps.cli.lanuse.library_top.authors_top',
                            'r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed'),

                           ('mps_cli_lanuse_default_persistency',
                            'mps.cli.lanuse.library_top.default_persistency',
                            'mps.cli.lanuse.library_second.default_persistency',
                            'mps.cli.lanuse.library_top.default_persistency.authors_top',
                            'r:ca00da79-915e-4bdb-9c30-11a341daf779'),

                           ('mps_cli_lanuse_binary',
                            'mps.cli.lanuse.library_top',
                            'mps.cli.lanuse.library_second',
                            'mps.cli.lanuse.library_top.authors_top',
                            'r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed')])
    def test_build_modules_and_models(self, test_data_location, library_top_solution_name, library_second_solution_name, library_top_authors_top_model_name, library_top_authors_top_model_uuid):
        """
        Test the building of modules and models
        """
        self.doSetUp(test_data_location)
        self.assertEqual(2, len(self.repo.solutions))

        library_top = self.repo.find_solution_by_name(library_top_solution_name)
        self.assertNotEqual(None, library_top)

        library_second = self.repo.find_solution_by_name(library_second_solution_name)
        self.assertNotEqual(None, library_second)

        library_top_authors_top = self.repo.find_model_by_name(library_top_authors_top_model_name)
        self.assertNotEqual(None, library_top_authors_top)
        self.assertEqual(library_top_authors_top_model_uuid, library_top_authors_top.uuid)

if __name__ == '__main__':
    unittest.main()
