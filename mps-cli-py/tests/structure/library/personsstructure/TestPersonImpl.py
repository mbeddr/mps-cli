from tests.structure.library.personsstructure.TestPerson import TestPerson


class TestPersonImpl(TestPerson):

    @staticmethod
    def get_concept_fqn():
        return "mps.cli.landefs.people.structure.Person"
