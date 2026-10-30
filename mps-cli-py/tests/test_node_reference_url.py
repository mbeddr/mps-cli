import unittest

from mpscli.model.NodeReferenceUrl import create_node_reference_url
from tests.test_base import TestBase


class TestNodeReferenceUrl(TestBase):

    def setUp(self):
        self.doSetUp("mps_cli_lanuse_file_per_root")
        self.model = self.repo.find_model_by_name(
            "mps.cli.lanuse.library_top.authors_top"
        )
        self.root = self.model.root_nodes[0]

    def test_create_default_url_for_numeric_node_id(self):
        url = create_node_reference_url(self.model, self.root)

        self.assertEqual(
            "http://127.0.0.1:63342/node?ref="
            "r%3Aec5f093b-9d83-43a1-9b41-b5952da8b1ed"
            "%28mps.cli.lanuse.library_top.authors_top%29"
            "%2F5731700211660045982",
            url,
        )

    def test_create_url_for_descendant_with_custom_port(self):
        person = self.root.get_children("persons")[0]

        url = create_node_reference_url(self.model, person, port=63320)

        self.assertEqual(
            "http://127.0.0.1:63320/node?ref="
            "r%3Aec5f093b-9d83-43a1-9b41-b5952da8b1ed"
            "%28mps.cli.lanuse.library_top.authors_top%29"
            "%2F5731700211660045983",
            url,
        )

    def test_reject_invalid_port(self):
        with self.assertRaises(ValueError):
            create_node_reference_url(self.model, self.root, port=65536)
