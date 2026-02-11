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

    def test_imports_loading(self):
        reader = SModelBuilderBinaryPersistency()
        model = reader.build(self.MPB_PATH)

        imported = reader.imported_models

        self.assertIsNotNone(imported)
        self.assertIsInstance(imported, dict)

        self.assertIn("0", imported)

        current = imported["0"]
        self.assertEqual(
            "r:cf91f372-8bfd-44b8-8e34-024eb23e64a8",
            current["uuid"],
        )
        self.assertEqual(
            "mps.cli.lanuse.library_top.binary_persistency.authors_top",
            current["name"],
        )

        self.assertGreaterEqual(len(imported), 1)

        for index, imp in imported.items():
            self.assertIn("uuid", imp)
            self.assertIn("name", imp)

            self.assertTrue(
                imp["uuid"].startswith("r:"),
                f"Invalid model uuid at index {index}",
            )

            self.assertIsInstance(imp["name"], str)
            self.assertGreater(len(imp["name"]), 0)

    def test_node_loading(self):
        reader = SModelBuilderBinaryPersistency()
        reader.build(self.MPB_PATH)

        self.assertGreater(len(reader.root_nodes), 0)

        root = reader.root_nodes[0]

        self.assertEqual(
            "mps.cli.landefs.people.structure.PersonsContainer",
            root["concept"],
        )

        self.assertEqual(
            "_010_classical_authors",
            root["properties"]["name"],
        )

        self.assertEqual(len(root["children"]), 2)

        first_child = root["children"][0]

        self.assertEqual(
            "mps.cli.landefs.people.structure.Person",
            first_child["concept"],
        )

        self.assertIn("name", first_child["properties"])
