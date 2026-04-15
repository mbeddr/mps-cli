import unittest

from mpscli.model.builder.SModelBuilderBinaryPersistency import (
    SModelBuilderBinaryPersistency,
)

MPB = (
    "../mps_test_projects/"
    "mps_cli_binary_persistency_generated_low_level_access_test_data/"
    "mps.cli.lanuse.library_top.binary_persistency.authors_top.mpb"
)
# PersonsContainer "_010_classical_authors"
ROOT_UUID = "4Yb5JA31NUu"
# Mark Twain
PERSON_UUID = "4Yb5JA31NUv"


def _all_nodes(model):
    result = []

    def _collect(node):
        result.append(node)
        for c in node.children or []:
            _collect(c)

    for r in model.root_nodes:
        _collect(r)
    return result


class TestNodeTree(unittest.TestCase):
    def setUp(self):
        builder = SModelBuilderBinaryPersistency()
        self.model = builder.build(MPB)
        self.root = self.model.root_nodes[0]

    def test_exactly_one_root(self):
        self.assertEqual(1, len(self.model.root_nodes))

    def test_root_concept(self):
        self.assertEqual(
            "mps.cli.landefs.people.structure.PersonsContainer",
            self.root.concept.name,
        )

    def test_root_uuid(self):
        self.assertEqual(ROOT_UUID, self.root.uuid)

    def test_root_name_property(self):
        self.assertEqual("_010_classical_authors", self.root.get_property("name"))

    def test_root_has_no_parent(self):
        self.assertIsNone(self.root.parent)

    def test_root_has_children(self):
        self.assertGreater(len(self.root.children), 0)

    def test_all_children_are_persons(self):
        for child in self.root.children:
            self.assertEqual(
                "mps.cli.landefs.people.structure.Person",
                child.concept.name,
            )

    def test_mark_twain_uuid(self):
        twain = next(
            (c for c in self.root.children if c.get_property("name") == "Mark Twain"),
            None,
        )
        self.assertIsNotNone(twain, "Mark Twain person node not found")
        self.assertEqual(PERSON_UUID, twain.uuid)

    def test_all_persons_have_name(self):
        for child in self.root.children:
            name = child.get_property("name")
            self.assertIsNotNone(name)
            self.assertGreater(len(name), 0)

    def test_parent_links(self):
        for child in self.root.children:
            self.assertIs(self.root, child.parent)

    def test_role_in_parent_set(self):
        for child in self.root.children:
            self.assertIsNotNone(child.role_in_parent)

    def test_all_nodes_have_string_uuid(self):
        for node in _all_nodes(self.model):
            self.assertIsInstance(node.uuid, str)
            self.assertGreater(len(node.uuid), 0)

    def test_node_uuids_are_encoded_not_raw_integers(self):
        for node in _all_nodes(self.model):
            self.assertFalse(
                node.uuid.isdigit(),
                f"uuid {node.uuid!r} looks like a raw integer - encoding not applied",
            )

    def test_all_nodes_have_dict_properties(self):
        for node in _all_nodes(self.model):
            self.assertIsInstance(node.properties, dict)

    def test_all_nodes_have_dict_references(self):
        for node in _all_nodes(self.model):
            self.assertIsInstance(node.references, dict)

    def test_all_nodes_have_list_children(self):
        for node in _all_nodes(self.model):
            self.assertIsInstance(node.children, list)

    def test_get_nodes_returns_all(self):
        self.assertEqual(len(_all_nodes(self.model)), len(self.model.get_nodes()))

    def test_get_node_by_uuid_root(self):
        found = self.model.get_node_by_uuid(ROOT_UUID)
        self.assertIs(self.root, found)

    def test_get_node_by_uuid_child(self):
        child = self.root.children[0]
        found = self.model.get_node_by_uuid(child.uuid)
        self.assertIs(child, found)

    def test_get_node_by_uuid_unknown_raises(self):
        # SModel.get_node_by_uuid() uses dict[key] and raises KeyError for missing keys
        with self.assertRaises(KeyError):
            self.model.get_node_by_uuid("dummy_uuid")
