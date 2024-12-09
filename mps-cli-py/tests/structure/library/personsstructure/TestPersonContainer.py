from mpscli.model.structure.AbstractSNodeWithStructure import AbstractSNodeWithStructure
from tests.structure.library.libstructure.TestINamedConcept import TestINamedConcept
from tests.structure.library.personsstructure.TestPerson import TestPerson


class TestPersonsContainer(AbstractSNodeWithStructure, TestINamedConcept):



    def persons(self) -> list[TestPerson]:
        return self.get_children("persons")

