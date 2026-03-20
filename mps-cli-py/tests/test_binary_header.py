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
MODEL_NAME = "mps.cli.lanuse.library_top.binary_persistency.authors_top"


class TestHeader(unittest.TestCase):
    def setUp(self):
        self.builder = SModelBuilderBinaryPersistency()
        self.model = self.builder.build(MPB)

    def test_model_uuid(self):
        self.assertEqual(MODEL_UUID, self.model.uuid)

    def test_model_uuid_not_placeholder(self):
        self.assertNotEqual("r:unknown", self.model.uuid)
        self.assertTrue(self.model.uuid.startswith("r:"))

    def test_model_name(self):
        self.assertEqual(MODEL_NAME, self.model.name)

    def test_model_name_not_placeholder(self):
        self.assertNotIn("unknown", self.model.name)

    def test_self_import_at_index_0(self):
        self.assertEqual(MODEL_UUID, self.builder.index_2_imported_model_uuid["0"])


if __name__ == "__main__":
    unittest.main()
