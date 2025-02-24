from mpscli.model.structure.AbstractSNodeInterfaceWithStructure import AbstractSNodeInterfaceWithStructure


class TestINamedConcept(AbstractSNodeInterfaceWithStructure):

    def name(self) -> str:
        return self.get_property("name")

