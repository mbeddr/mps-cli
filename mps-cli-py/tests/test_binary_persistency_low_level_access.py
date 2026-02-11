from mpscli.model.builder.SModelBuilderBinaryPersistency import (
    SModelBuilderBinaryPersistency,
)
from tests.test_base import TestBase
from mpscli.model.SRepository import SRepository
from mpscli.model.builder.binary.reader import BinaryReader
from mpscli.model.builder.binary.constants import NODEID_LONG
from mpscli.model.builder.binary.nodes import read_node


class TestBinaryPersistencyLowLevelAccess(TestBase):

    MPB_PATH = (
        "../mps_test_projects/"
        "mps_cli_binary_persistency_generated_low_level_access_test_data/"
        "mps.cli.lanuse.library_top.binary_persistency.authors_top.mpb"
    )

    def test_model_header_parsed(self):
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

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
        builder.build(self.MPB_PATH)

        self.assertIn("0", builder.index_2_imported_model_uuid)

        self.assertEqual(
            "r:cf91f372-8bfd-44b8-8e34-024eb23e64a8",
            builder.index_2_imported_model_uuid["0"],
        )

    def test_node_structure(self):
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

    def test_parent_and_roles_integrity(self):
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        root = model.root_nodes[0]
        child = root.children[0]

        self.assertIs(child.parent, root)
        self.assertIsNotNone(child.role_in_parent)

    def test_model_traversal(self):
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        nodes = model.get_nodes()
        self.assertGreater(len(nodes), 0)

        root = model.root_nodes[0]
        found = model.get_node_by_uuid(root.uuid)

        self.assertEqual(root.uuid, found.uuid)

    def test_reference_resolution(self):
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        repo = SRepository()
        repo.solutions = []
        repo.uuid_2_model = {model.uuid: model}

        for node in model.get_nodes():
            for ref in node.references.values():
                resolved = ref.resolve(repo)
                self.assertTrue(resolved is None or hasattr(resolved, "uuid"))

    def test_reference_model_uuid_format(self):
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        for node in model.get_nodes():
            for ref in node.references.values():
                self.assertTrue(ref.model_uuid.startswith("r:"))

    def test_node_id_encoding_applied(self):
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        for node in model.get_nodes():
            self.assertIsInstance(node.uuid, str)

    def test_invalid_reference_kind_raises(self):
        data = bytearray()
        data.extend((0).to_bytes(2, "big"))
        data.append(NODEID_LONG)
        data.extend((1).to_bytes(8, "big"))
        data.extend((0).to_bytes(2, "big"))
        data.append(ord("{"))
        data.extend((0).to_bytes(2, "big"))
        data.extend((0).to_bytes(2, "big"))
        data.extend((1).to_bytes(2, "big"))
        data.extend((0).to_bytes(2, "big"))
        data.append(9)

        reader = BinaryReader(bytes(data))
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        with self.assertRaises(ValueError):
            read_node(reader, builder, model)

    def test_binary_parsing_performance(self):
        import time

        builder = SModelBuilderBinaryPersistency()

        start = time.time()
        builder.build(self.MPB_PATH)
        end = time.time()

        self.assertLess(end - start, 2)
