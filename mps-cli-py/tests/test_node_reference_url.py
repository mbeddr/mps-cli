import unittest

from mpscli.model.NodeReferenceUrl import create_node_reference_url


class TestNodeReferenceUrl(unittest.TestCase):

    def test_create_default_url_for_numeric_node_id(self):
        url = create_node_reference_url(
            "r:de74548a-01ae-41ea-9d0d-56cf4b0072f0",
            "tech.cariad.e3_1_2_solution.hcp2.software_elements",
            "1MPPnnOfw3d",
        )

        self.assertEqual(
            "http://127.0.0.1:63342/node?ref="
            "r%3Ade74548a-01ae-41ea-9d0d-56cf4b0072f0"
            "%28tech.cariad.e3_1_2_solution.hcp2.software_elements%29"
            "%2F2068794306432205005",
            url,
        )

    def test_create_url_with_custom_port_and_string_node_id(self):
        url = create_node_reference_url(
            "r:model-id", "model name", "~generated_node", port=63320
        )

        self.assertEqual(
            "http://127.0.0.1:63320/node?ref="
            "r%3Amodel-id%28model+name%29%2F~generated_node",
            url,
        )

    def test_reject_invalid_port(self):
        with self.assertRaises(ValueError):
            create_node_reference_url("r:model-id", "model", "1MPPnnOfw3d", port=65536)
