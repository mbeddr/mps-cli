

class SModel:

    def __init__(self, name, uuid, is_do_not_generate):
        self.name = name
        self.uuid = uuid
        self.root_nodes = []
        self.path_to_model_file = ""
        self.is_do_not_generate = is_do_not_generate

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