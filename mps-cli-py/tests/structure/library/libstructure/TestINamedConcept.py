from abc import ABC

from mpscli.model.structure.SNodeStructure import AbstractSNodeInterfaceWithStructure


class TestINamedConcept(ABC, AbstractSNodeInterfaceWithStructure):

    def name(self) -> str:
        return self.get_property("name")

