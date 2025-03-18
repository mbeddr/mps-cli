from abc import ABC
from mpscli.model.SNode import SNode
from mpscli.model.structure.SNodeConceptDeclaration import SNodeConceptDeclaration


class AbstractSNodeWithStructure(SNodeConceptDeclaration):

    def __init__(self, uuid, concept, role_in_parent, parent, repo):
        super().__init__(uuid,concept, role_in_parent, parent)
        self.repo = repo
