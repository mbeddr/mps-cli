from tests.structure.library.personsstructure.TestPersonContainer import TestPersonsContainer


class TestPersonsContainerImpl(TestPersonsContainer):
    @staticmethod
    def get_concept_fqn():
        return "mps.cli.landefs.people.structure.PersonsContainer"
