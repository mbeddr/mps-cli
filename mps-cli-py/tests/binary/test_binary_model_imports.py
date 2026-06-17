import unittest

from parameterized import parameterized

from tests.test_base import TestBase


class TestBinaryModelImports(TestBase):

    @parameterized.expand(
        [
            (
                "mps_cli_binary_persistency_generated",
                "mps.cli.lanuse.library_top.binary_persistency.library_top",
                "r:cf91f372-8bfd-44b8-8e34-024eb23e64a8",
            ),
        ]
    )
    def test_model_imports(self, test_data_location, model_name, imported_model_uuid):
        self.doSetUp(test_data_location)

        model = self.repo.find_model_by_name(model_name)
        self.assertNotEqual(None, model)
        self.assertIsInstance(model.imported_models, dict)
        self.assertIn(imported_model_uuid, model.imported_models.values())