class NodeIdEncodingUtils:

    @staticmethod
    def encode(node_id: str) -> str:
        if node_id.isdigit():
            return node_id

        return node_id
