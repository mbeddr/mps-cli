
from mpscli.model.structure.AbstractSNodeWithStructure import AbstractSNodeInterfaceWithStructure


class TestINamedConcept(AbstractSNodeInterfaceWithStructure):

    def name(self) -> str:
        return self.get_property("name")

