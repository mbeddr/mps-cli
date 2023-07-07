

class SModel:

    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid
        self.root_nodes = []
        self.path_to_model_file = ""

    def get_nodes(self):
        res = []
        for r in self.root_nodes:
            res.append(r)
            res.extend(r.get_descendants())
        return res

    def get_node_by_uuid(self, uuid):
        for n in self.get_nodes():
            if n.uuid == uuid:
                return n
        return None