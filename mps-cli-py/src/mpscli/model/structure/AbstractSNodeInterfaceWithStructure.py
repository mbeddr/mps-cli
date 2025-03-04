from abc import ABC

from mpscli.model.SNode import SNode
from mpscli.model.structure.SNodeConceptDeclaration import PythonConceptDeclaration


class AbstractSNodeInterfaceWithStructure(SNode, metaclass=PythonConceptDeclaration):
    pass
