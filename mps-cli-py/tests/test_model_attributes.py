import unittest

from parameterized import parameterized
from tests.test_base import TestBase


class TestModelAttributes(TestBase):

    @parameterized.expand([('mps_cli_lanuse_model_attributes',
                            'mps_cli_lanuse_model_attributes',
                            'mps_cli_lanuse_model_attributes.default_generation',
                            'mps_cli_lanuse_model_attributes.disable_generation',
                            'mps_cli_lanuse_model_attributes.enable_generation')])
    def test_model_attributes(self, test_data_location, solution_name, first_model, second_model, third_model):
        """
        Test the building of modules and models
        """
        self.doSetUp(test_data_location)
        self.assertEqual(1, len(self.repo.solutions))

        solution = self.repo.find_solution_by_name(solution_name)
        self.assertNotEqual(None, solution)

        model = self.repo.find_model_by_name(first_model)
        self.assertNotEqual(None, model)
        self.assertFalse(model.is_do_not_generate)

        model = self.repo.find_model_by_name(second_model)
        self.assertNotEqual(None, model)
        self.assertTrue(model.is_do_not_generate)

        model = self.repo.find_model_by_name(third_model)
        self.assertNotEqual(None, model)
        self.assertFalse(model.is_do_not_generate)

if __name__ == '__main__':
    unittest.main()
