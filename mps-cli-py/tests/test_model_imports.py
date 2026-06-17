import unittest

from parameterized import parameterized

from tests.test_base import TestBase


class TestModelImports(TestBase):

    @parameterized.expand(
        [
            (
                "mps_cli_lanuse_file_per_root",
                "mps.cli.lanuse.library_top.library_top",
                "r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed",
            ),
            (
                "mps_cli_lanuse_default_persistency",
                "mps.cli.lanuse.library_top.default_persistency.library_top",
                "r:ca00da79-915e-4bdb-9c30-11a341daf779",
            ),
        ]
    )
    def test_model_imports(self, test_data_location, model_name, imported_model_uuid):
        self.doSetUp(test_data_location)

        model = self.repo.find_model_by_name(model_name)
        self.assertNotEqual(None, model)
        self.assertIsInstance(model.imported_models, dict)
        self.assertIn(imported_model_uuid, model.imported_models.values())