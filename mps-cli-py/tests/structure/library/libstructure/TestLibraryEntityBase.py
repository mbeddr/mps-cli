from abc import ABC

from mpscli.model.structure.SNodeStructure import AbstractSNodeWithStructure
from tests.structure.library.libstructure.TestINamedConcept import TestINamedConcept


class TestLibraryEntityBase(AbstractSNodeWithStructure, TestINamedConcept):

    def isbn(self) -> str:
        return self.get_property("isbn")

    def available(self) -> bool:
        return self.get_property("available")

class TestLibraryEntityBaseImpl(TestLibraryEntityBase):
    @staticmethod
    def get_concept_fqn():
        return "mps.cli.landefs.library.structure.LibraryEntityBase"