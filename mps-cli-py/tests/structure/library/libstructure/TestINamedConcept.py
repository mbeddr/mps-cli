from mpscli.model.structure.AbstractSNodeWithStructure import AbstractSNodeWithStructure


class TestINamedConcept(AbstractSNodeWithStructure):

    def name(self) -> str:
        return self.get_property("name")

