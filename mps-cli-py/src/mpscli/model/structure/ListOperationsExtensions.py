from mpscli.model.SNode import NodeList


def of_concept(self, concept_class):
    return NodeList(item for item in self if isinstance(item, concept_class))

def is_empty(self):
    return not self

def is_not_empty(self):
    return not self.is_empty()

def where(self, condition):
    return NodeList(node for node in self if condition(node))

def select(self, function):
    return NodeList(function(node) for node in self)

def select_many(self, function):
    return self.flatten(self).select(function)

def flatten(self, node_or_list):
    if isinstance(node_or_list, NodeList):
        return NodeList(node for sublist in node_or_list for node in self.flatten(sublist))
    return NodeList([node_or_list])

def for_each(self, function):
    for node in self:
        function(node)

def add_list_operation_extensions():
    setattr(NodeList, 'of_concept', of_concept)
    setattr(NodeList, 'is_empty', is_empty)
    setattr(NodeList, 'is_not_empty', is_not_empty)
    setattr(NodeList, 'where', where)
    setattr(NodeList, 'select', select)
    setattr(NodeList, 'select_many', select_many)
    setattr(NodeList, 'flatten', flatten)
    setattr(NodeList, 'for_each', for_each)

