from mpscli.model.builder.SModelBuilderBinaryPersistency import (
    SModelBuilderBinaryPersistency,
)
from tests.test_base import TestBase
from mpscli.model.SRepository import SRepository
from mpscli.model.builder.binary.model_input_stream import ModelInputStream
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

    def test_invalid_reference_model_kind_handled_gracefully(self):
        # model_kind = 9 is unknown
        # _read_reference handles unknown model_kind by reading the resolve_info string and
        # returning a (ref_name, placeholder) so no exception raised.
        data = bytearray()
        # props_count = 0
        data.extend((0).to_bytes(2, "big"))
        # node_id_kind for this node
        data.append(NODEID_LONG)
        # node_id = 1
        data.extend((1).to_bytes(8, "big"))
        # concept_index
        data.extend((0).to_bytes(2, "big"))
        # opening brace
        data.append(ord("{"))
        # inner props count = 0
        data.extend((0).to_bytes(2, "big"))
        # consumed as u16 by read_node
        data.extend((0).to_bytes(2, "big"))
        # ref_count = 1
        data.extend((1).to_bytes(2, "big"))
        # ref_index = 0
        data.extend((0).to_bytes(2, "big"))
        # skip byte (always 0x01)
        data.append(0x01)
        # node_id_kind for reference target
        data.append(NODEID_LONG)
        # node_id for reference target = 1
        data.extend((1).to_bytes(8, "big"))
        # model_kind = 9 (unknown)
        data.append(9)
        # resolve_info = null string
        data.append(0x70)
        # read_children reads child_count as u32, then read_node reads closing brace
        data.extend((0).to_bytes(4, "big"))
        # closing brace
        data.append(ord("}"))

        reader = ModelInputStream(bytes(data))
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        node = read_node(reader, builder, model)
        self.assertIsNotNone(node)

    def test_binary_parsing_performance(self):
        import time

        builder = SModelBuilderBinaryPersistency()

        start = time.time()
        builder.build(self.MPB_PATH)
        end = time.time()

        self.assertLess(end - start, 2)

    def test_unknown_reference_model_kind_returns_placeholder(self):
        # model_kind = 2 is also unknown so same graceful handling has been implemented where it
        # returns placeholder and no exception is raised
        data = bytearray()
        # props_count = 0
        data.extend((0).to_bytes(2, "big"))
        # node_id_kind for this node
        data.append(NODEID_LONG)
        # node_id = 1
        data.extend((1).to_bytes(8, "big"))
        # concept_index
        data.extend((0).to_bytes(2, "big"))
        # opening brace
        data.append(ord("{"))
        # inner props count = 0
        data.extend((0).to_bytes(2, "big"))
        # consumed as u16 by read_node
        data.extend((0).to_bytes(2, "big"))
        # ref_count = 1
        data.extend((1).to_bytes(2, "big"))
        # ref_index = 0
        data.extend((0).to_bytes(2, "big"))
        # skip byte (always 0x01)
        data.append(0x01)
        # node_id_kind for reference target
        data.append(NODEID_LONG)
        # node_id for reference target = 1
        data.extend((1).to_bytes(8, "big"))
        # model_kind = 2 (unknown)
        data.append(2)
        # resolve_info = null string
        data.append(0x70)
        # read_children reads child_count as u32, then read_node reads closing brace
        data.extend((0).to_bytes(4, "big"))
        # closing brace
        data.append(ord("}"))

        reader = ModelInputStream(bytes(data))
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        builder.index_2_reference_role["0"] = "person"

        node = read_node(reader, builder, model)
        self.assertIsNotNone(node)

    def test_reference_has_resolve_info_field(self):
        builder = SModelBuilderBinaryPersistency()
        model = builder.build(self.MPB_PATH)

        for node in model.get_nodes():
            for ref in node.references.values():
                self.assertTrue(hasattr(ref, "resolve_info"))
