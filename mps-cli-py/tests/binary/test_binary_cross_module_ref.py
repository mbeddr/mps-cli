import sys
import unittest

sys.path.insert(1, "../..")

from mpscli.model.builder.SModelBuilderBinaryPersistency import (
    SModelBuilderBinaryPersistency,
)

# migration.mpb extracted from org.iets3.protocol.transport-src.jar of vemb repo
# this file contains MODELID_REGULAR inline cross-module model references which previously caused
# stream misalignment due to read_string() being called where the binary format requires read_module_ref()
MPB = (
    "../mps_test_projects/"
    "mps_cli_binary_persistency_cross_module_ref/"
    "migration.mpb"
)

EXPECTED_MODEL_NAME = "org.iets3.protocol.transport.migration"


class TestCrossModuleModelRef(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = SModelBuilderBinaryPersistency().build(MPB)

    def test_parses_without_error(self):
        # if the model object exists the parse completed without raising
        self.assertIsNotNone(self.model)

    def test_model_name_is_set(self):
        self.assertEqual(
            EXPECTED_MODEL_NAME,
            self.model.name,
            "model name should match the migration model from the transport language",
        )

    def test_model_uuid_is_set(self):
        self.assertIsNotNone(self.model.uuid)
        self.assertNotEqual("", self.model.uuid)
        self.assertNotEqual("r:unknown", self.model.uuid)

    def test_model_has_root_nodes(self):
        # root nodes being present provess that the node tree was parsed correctly after the
        # cross-module model reference..
        self.assertGreater(
            len(self.model.root_nodes),
            0,
            "migration model should have at least one root node",
        )


if __name__ == "__main__":
    unittest.main()
