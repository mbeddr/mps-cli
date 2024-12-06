from tests.structure.library.libstructure.TestBook import TestBook


class TestBookImpl(TestBook):
    @staticmethod
    def get_concept_fqn():
        return "mps.cli.landefs.library.structure.Book"
