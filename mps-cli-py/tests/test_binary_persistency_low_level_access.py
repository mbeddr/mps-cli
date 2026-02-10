from mpscli.model.builder.SModelBuilderBinaryPersistency import (
    SModelBuilderBinaryPersistency,
)
from tests.test_base import TestBase


class TestBinaryPersistencyLowLevelAccess(TestBase):

    MPB_PATH = (
        "../mps_test_projects/"
        "mps_cli_binary_persistency_generated_low_level_access_test_data/"
        "mps.cli.lanuse.library_top.binary_persistency.authors_top.mpb"
    )

    def test_read_model_reference_from_binary(self):
        path_to_model = (
            "../mps_test_projects/"
            "mps_cli_binary_persistency_generated_low_level_access_test_data/"
            "mps.cli.lanuse.library_top.binary_persistency.authors_top.mpb"
        )

        reader = SModelBuilderBinaryPersistency()
        model = reader.build(self.MPB_PATH)

        self.assertIsNotNone(model)

        self.assertEqual("r:cf91f372-8bfd-44b8-8e34-024eb23e64a8", model["uuid"])

        self.assertEqual(
            "mps.cli.lanuse.library_top.binary_persistency.authors_top", model["name"]
        )

    def test_registry_loading(self):
        reader = SModelBuilderBinaryPersistency()
        reader.build(self.MPB_PATH)

        registry = reader.registry

        # registry sections
        self.assertIn("concepts", registry)
        self.assertIn("properties", registry)
        self.assertIn("references", registry)
        self.assertIn("containments", registry)

        # concepts (value-based check)
        concept_names = {c["name"] for c in registry["concepts"].values()}
        self.assertIn("mps.cli.landefs.people.structure.Person", concept_names)
        self.assertIn("jetbrains.mps.lang.core.structure.INamedConcept", concept_names)

        # properties
        property_names = {p["name"] for p in registry["properties"].values()}
        self.assertIn("name", property_names)
