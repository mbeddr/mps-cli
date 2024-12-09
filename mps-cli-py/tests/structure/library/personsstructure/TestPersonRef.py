from mpscli.model.structure.AbstractSNodeWithStructure import AbstractSNodeWithStructure
from tests.structure.library.personsstructure.TestPerson import TestPerson


class TestPersonRef(AbstractSNodeWithStructure):

    def person(self) -> TestPerson:
        return self.get_reference("person")

class TestPersonRefImpl(TestPersonRef):
    @staticmethod
    def get_concept_fqn():
        return "mps.cli.landefs.people.structure.PersonRef"