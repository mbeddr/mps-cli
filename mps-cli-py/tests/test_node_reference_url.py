import unittest

from mpscli.model.NodeReferenceUrl import create_node_reference_url
from mpscli.model.SModel import SModel
from mpscli.model.SNode import SNode


class TestNodeReferenceUrl(unittest.TestCase):

    def test_create_default_url_for_numeric_node_id(self):
        model = SModel(
            "tech.cariad.e3_1_2_solution.hcp2.software_elements",
            "r:de74548a-01ae-41ea-9d0d-56cf4b0072f0",
            False,
        )
        node = SNode("1MPPnnOfw3d", None, None, None)

        url = create_node_reference_url(model, node)

        self.assertEqual(
            "http://127.0.0.1:63342/node?ref="
            "r%3Ade74548a-01ae-41ea-9d0d-56cf4b0072f0"
            "%28tech.cariad.e3_1_2_solution.hcp2.software_elements%29"
            "%2F2068794306432205005",
            url,
        )

    def test_create_url_with_custom_port_and_string_node_id(self):
        model = SModel("model name", "r:model-id", False)
        root = SNode("root", None, None, None)
        node = SNode("~generated_node", None, "children", root)
        root.children.append(node)
        model.root_nodes.append(root)

        url = create_node_reference_url(model, node, port=63320)

        self.assertEqual(
            "http://127.0.0.1:63320/node?ref="
            "r%3Amodel-id%28model+name%29%2F~generated_node",
            url,
        )

    def test_reject_invalid_port(self):
        model = SModel("model", "r:model-id", False)
        node = SNode("1MPPnnOfw3d", None, None, None)

        with self.assertRaises(ValueError):
            create_node_reference_url(model, node, port=65536)
