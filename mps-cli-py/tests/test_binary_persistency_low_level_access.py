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
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        self.assertIsNotNone(model)

        self.assertEqual(
            "r:cf91f372-8bfd-44b8-8e34-024eb23e64a8",
            model.uuid,
        )

        self.assertEqual(
            "mps.cli.lanuse.library_top.binary_persistency.authors_top",
            model.name,
        )

    def test_registry_loading(self):
        builder = SModelBuilderBinaryPersistency()
        builder.build(self.MPB_PATH)

        self.assertGreater(len(builder.index_2_concept), 0)
        self.assertGreater(len(builder.index_2_property), 0)

        concept_names = [c.name for c in builder.index_2_concept.values()]

        self.assertIn(
            "mps.cli.landefs.people.structure.Person",
            concept_names,
        )

        self.assertIn(
            "jetbrains.mps.lang.core.structure.INamedConcept",
            concept_names,
        )

    def test_imports_loading(self):
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        self.assertIn("0", builder.index_2_imported_model_uuid)

        self.assertEqual(
            "r:cf91f372-8bfd-44b8-8e34-024eb23e64a8",
            builder.index_2_imported_model_uuid["0"],
        )

    def test_node_loading(self):
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        self.assertGreater(len(model.root_nodes), 0)

        root = model.root_nodes[0]

        self.assertEqual(
            "mps.cli.landefs.people.structure.PersonsContainer",
            root.concept.name,
        )

        self.assertEqual(
            "_010_classical_authors",
            root.get_property("name"),
        )

        self.assertEqual(len(root.children), 2)

        first_child = root.children[0]

        self.assertEqual(
            "mps.cli.landefs.people.structure.Person",
            first_child.concept.name,
        )

        self.assertIsNotNone(first_child.get_property("name"))
