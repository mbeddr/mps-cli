from abc import ABC

from mpscli.model.SNode import SNode


def collect_base_classes(cls, collected_classes):
    if cls not in collected_classes:
        collected_classes.append(cls)
        for base_class in cls.__bases__:
            collect_base_classes(base_class, collected_classes)
    return collected_classes

class PythonConceptDeclaration(type):
    def mro(cls):
        return collect_base_classes(cls, [])

class SNodeConceptDeclaration(SNode, metaclass=PythonConceptDeclaration):
    pass