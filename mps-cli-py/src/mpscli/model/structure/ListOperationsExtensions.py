from mpscli.model.SNode import NodeList


def of_concept(self, concept_class):
    return NodeList(item for item in self if isinstance(item, concept_class))

def is_empty(self):
    return not self

def is_not_empty(self):
    return not self.is_empty()

def where(self, condition):
    return NodeList(node for node in self if condition)

def add_list_operation_extensions():
    setattr(NodeList, 'of_concept', of_concept)
    setattr(NodeList, 'is_empty', of_concept)
    setattr(NodeList, 'is_not_empty', of_concept)
    setattr(NodeList, 'where', where)

