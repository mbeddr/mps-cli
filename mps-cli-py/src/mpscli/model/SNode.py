
class SNode:

    def __init__(self, uuid, concept, role_in_parent):
        self.uuid = uuid
        self.concept = concept
        self.role_in_parent = role_in_parent
        self.properties = {}
        self.references = {}
        self.children = []

    def get_property(self, name):
        return self.properties.get(name)

    def get_reference(self, name):
        return self.references[name]

    def get_children(self, role):
        return list(filter(lambda c : c.role_in_parent == role, self.children))

    def get_descendants(self):
        res = []
        self.__do_collect_descendants(self, res)
        return res

    def __do_collect_descendants(self, node, res):
        res.extend(node.children)
        for c in node.children:
            self.__do_collect_descendants(c, res)

