from mpscli.model.structure.SNodeStructure import AbstractSNodeWithStructure
from tests.structure.library.libstructure.TestINamedConcept import TestINamedConcept
from tests.structure.library.libstructure.TestLibraryEntityBase import TestLibraryEntityBase


class TestLibrary(AbstractSNodeWithStructure, TestINamedConcept):

    @staticmethod
    def get_concept_fqn():
        return "mps.cli.landefs.library.structure.Library"

    def entities(self) -> list[TestLibraryEntityBase]:
        return self.get_children("entities")


