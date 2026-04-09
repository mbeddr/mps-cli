import unittest

from mpscli.model.builder.SSolutionsRepositoryBuilder import (
    SSolutionsRepositoryBuilder,
)

REPO_PATH = "../mps_test_projects/mps_cli_binary_persistency_generated/"
LIB_MODEL_NAME = "mps.cli.lanuse.library_top.binary_persistency.library_top"
MARK_TWAIN_UUID = "4Yb5JA31NUv"


def _build_repo():
    builder = SSolutionsRepositoryBuilder()
    builder.USE_CACHE = False
    return builder.build(REPO_PATH)


class TestCrossModelReferenceResolution(unittest.TestCase):
    def setUp(self):
        self.repo = _build_repo()
        lib = self.repo.find_model_by_name(LIB_MODEL_NAME)
        self.assertIsNotNone(lib)
        munich = next(
            r for r in lib.root_nodes if r.get_property("name") == "munich_library"
        )
        # Tom Sawyer
        book = munich.get_children("entities")[0]
        authors = book.get_children("authors")
        self.assertGreater(len(authors), 0)
        self.ref = authors[0].get_reference("person")
        self.lib = lib

    def test_reference_not_none(self):
        self.assertIsNotNone(self.ref)

    def test_resolve_info_is_mark_twain(self):
        self.assertEqual("Mark Twain", self.ref.resolve_info)

    def test_model_uuid_format(self):
        self.assertTrue(self.ref.model_uuid.startswith("r:"))

    def test_node_uuid(self):
        self.assertEqual(MARK_TWAIN_UUID, self.ref.node_uuid)

    def test_resolve_returns_node(self):
        self.assertIsNotNone(self.ref.resolve(self.repo))

    def test_resolved_node_is_mark_twain(self):
        resolved = self.ref.resolve(self.repo)
        self.assertEqual("Mark Twain", resolved.get_property("name"))

    def test_resolved_node_concept(self):
        resolved = self.ref.resolve(self.repo)
        self.assertEqual(
            "mps.cli.landefs.people.structure.Person",
            resolved.concept.name,
        )

    def test_resolved_node_uuid_matches(self):
        resolved = self.ref.resolve(self.repo)
        self.assertEqual(MARK_TWAIN_UUID, resolved.uuid)

    def test_all_lib_references_have_r_uuid(self):
        for node in self.lib.get_nodes():
            for ref in node.references.values():
                self.assertTrue(
                    ref.model_uuid.startswith("r:"),
                    f"Reference model_uuid {ref.model_uuid!r} not in r: format",
                )

    def test_all_lib_references_have_resolve_info_attr(self):
        for node in self.lib.get_nodes():
            for ref in node.references.values():
                self.assertTrue(hasattr(ref, "resolve_info"))


if __name__ == "__main__":
    unittest.main()
