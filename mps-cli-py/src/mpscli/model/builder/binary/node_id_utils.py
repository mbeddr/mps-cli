# mpscli/model/builder/node_id_utils.py
class NodeIdEncodingUtils:
    @staticmethod
    def encode(node_id: str) -> str:
        if node_id is None:
            return None

        if node_id.isdigit():
            return str(int(node_id))

        return node_id
