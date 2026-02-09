from mpscli.model.builder.SModelBuilderBinaryPersistency import SModelBuilderBinaryPersistency
from tests.test_base import TestBase


class TestBinaryPersistencyLowLevelAccess(TestBase):

    def test_read_model_reference_from_binary(self):
        path_to_model = (
            "../mps_test_projects/"
            "mps_cli_binary_persistency_generated_low_level_access_test_data/"
            "mps.cli.lanuse.library_top.binary_persistency.authors_top.mpb"
        )

        reader = SModelBuilderBinaryPersistency()
        model = reader.build(path_to_model)

        self.assertIsNotNone(model)

        self.assertEqual(
            "r:cf91f372-8bfd-44b8-8e34-024eb23e64a8",
            model["uuid"]
        )

        self.assertEqual(
            "mps.cli.lanuse.library_top.binary_persistency.authors_top",
            model["name"]
        )
