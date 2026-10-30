from urllib.parse import urlencode

from mpscli.model.builder.utils.NodeIdEncodingUtils import NodeIdEncodingUtils

DEFAULT_MPS_PORT = 63342
_NODE_ID_ENCODING_UTILS = NodeIdEncodingUtils()


def create_node_reference_url(model, node, port=DEFAULT_MPS_PORT):
    """Create a local MPS node URL for a node in the given model."""
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("port must be an integer between 1 and 65535")

    try:
        node_id = _NODE_ID_ENCODING_UTILS.decode(node.uuid)
    except ValueError:
        node_id = node.uuid

    model_reference = "{}({})".format(model.uuid, model.name)
    reference = "{}/{}".format(model_reference, node_id)
    return "http://127.0.0.1:{}/node?{}".format(port, urlencode({"ref": reference}))
