import unittest

from parameterized import parameterized

from mpscli.model.structure.SNodeStructure import AbstractSNodeWithStructure
from mpscli.model.structure.StructureAwareSNodeClassFinder import StructureAwareSNodeClassFinder
from tests.structure.library.libstructure.TestBook import TestBook
from tests.structure.library.libstructure.TestINamedConcept import TestINamedConcept
from tests.structure.library.libstructure.TestLibraryEntityBase import TestLibraryEntityBase
from tests.structure.library.personsstructure.TestPerson import TestPerson
from tests.test_base import TestBase


class TestParseWithStructureAwareClasses(TestBase):

    @parameterized.expand(['mps_cli_lanuse_file_per_root',
                           'mps_cli_lanuse_default_persistency',
                           'mps_cli_lanuse_binary'])
    def test_parse_with_structure_aware_concepts(self, test_data_location):
        # given + when we have an initialized finder
        snode_finder = StructureAwareSNodeClassFinder(".")
        self.doSetUp(test_data_location, snode_finder)

        # then expect to have some instances of the classes
        nodes = self.repo.get_nodes()

        self.assert_concept_occurence(TestBook, 3)
        self.assert_concept_occurence(AbstractSNodeWithStructure, 9, False)
        self.assert_concept_occurence(TestINamedConcept, 9)
        self.assert_concept_occurence(TestPerson, 1)

    def assert_concept_occurence(self, clazz, min_occurrence, print_names=True):
        nodes = self.repo.get_nodes()
        instances = [item for item in nodes if isinstance(item, clazz)]
        if print_names:
            print([instance.name() for instance in instances])
        self.assertTrue(len(instances) > min_occurrence, f"expected at least {min_occurrence} instances, but found {len(instances)}")


if __name__ == '__main__':
    unittest.main()