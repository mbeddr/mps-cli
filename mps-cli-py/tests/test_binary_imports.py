import unittest

from mpscli.model.builder.SModelBuilderBinaryPersistency import (
    SModelBuilderBinaryPersistency,
)

MPB = (
    "../mps_test_projects/"
    "mps_cli_binary_persistency_generated_low_level_access_test_data/"
    "mps.cli.lanuse.library_top.binary_persistency.authors_top.mpb"
)
MODEL_UUID = "r:cf91f3728bfd44b88e34024eb23e64a8"


class TestImports(unittest.TestCase):
    def setUp(self):
        self.builder = SModelBuilderBinaryPersistency()
        self.builder.build(MPB)

    def test_import_0_is_self(self):
        self.assertEqual(MODEL_UUID, self.builder.index_2_imported_model_uuid["0"])

    def test_non_empty_imports_start_with_r_colon(self):
        for key, uid in self.builder.index_2_imported_model_uuid.items():
            if uid:  # empty string is valid for foreign/stub imports
                self.assertTrue(
                    uid.startswith("r:"),
                    f"Import[{key}]={uid!r} does not start with 'r:'",
                )


if __name__ == "__main__":
    unittest.main()
