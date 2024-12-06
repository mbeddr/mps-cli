from tests.structure.library.libstructure.TestEPeriodicity import TestEPeriodicity
from tests.structure.library.libstructure.TestLibraryEntityBase import TestLibraryEntityBase


class TestMagazine(TestLibraryEntityBase):


    def periodicity(self) -> TestEPeriodicity:
        value = self.get_property("periodicity")
        index = value.rfind('/')
        return TestEPeriodicity(value[index + 1:])

class TestMagazineImpl(TestMagazine):
    @staticmethod
    def get_concept_fqn():
        return "mps.cli.landefs.library.structure.Magazine"