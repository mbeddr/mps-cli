from tests.structure.library.libstructure.TestLibrary import TestLibrary


class TestLibraryImpl(TestLibrary):

    @staticmethod
    def get_concept_fqn():
        return "mps.cli.landefs.library.structure.Library"
