import importlib
import shutil
import sys
import unittest
import os

from parameterized import parameterized

from mpscli.model.structure.StructureAwareSNodeClassFinder import StructureAwareSNodeClassFinder
from mpscli.structuregen.gen.StructureFromLanguageGenerator import StructureFromLanguageGenerator
from tests.test_base import TestBase

CLASS_OUTPUT_FOLDER = "../../../../target_gen"

class TestLanguageStructureGenerator(TestBase):

    def test_building_languages(self):
        # given: the path to language definition, the concepts to generate, and an empty folder
        language_path = "../../../mps_test_projects/mps_cli_landefs"
        path_to_mps = os.getenv('path_to_mps') + "/languages/languageDesign/structure"
        path_to_core_lang = os.getenv('path_to_mps') + "/languages/core/core"
        concepts_to_generate = {'mps.cli.landefs.library.structure.Library', 'mps.cli.landefs.library.structure.Book',
                                'mps.cli.landefs.library.structure.Magazine', 'mps.cli.landefs.people.structure.PersonsContainer'}

        try:
            shutil.rmtree(CLASS_OUTPUT_FOLDER)
        except Exception:
            pass

        # when: the generator is created and executed
        structure_generator = StructureFromLanguageGenerator.init_generate_concepts([path_to_mps, path_to_core_lang, language_path], concepts_to_generate, CLASS_OUTPUT_FOLDER)
        number_of_generated_classes = structure_generator.generate_classes()

        # then: we should have the expected class hierarchy
        self.assertEqual(number_of_generated_classes, 11, "Wrong number of classes created")

    def test_smoke_class_exist(self):
        # given: the generated classes from the first test case and the sys path is modified accordingly
        sys.path.append(CLASS_OUTPUT_FOLDER)

        # when: an instance of the library is created
        lib_module = importlib.import_module('mps.cli.landefs.library.structure.Library')
        lib_class = lib_module.Library
        lib = lib_class("1234", "mps.cli.landefs.library.structure.Library", None, None, None)

        # then: it should be there with the name
        self.assertEqual(lib.alias(), "library", "Instanciating the class is not working correctly")

    @parameterized.expand(['mps_cli_lanuse_file_per_root',
                           'mps_cli_lanuse_default_persistency',
                           'mps_cli_lanuse_binary'])
    def test_using_classes(self, test_data_location):
        # given: the generated classes from the first test case in the class output folder and the repo to load
        snode_finder = StructureAwareSNodeClassFinder(CLASS_OUTPUT_FOLDER)

        # when: the repo is set up and loaded
        self.doSetUp(test_data_location, snode_finder)

        # then: the generated classes can be used and information can be retrieved

        nodes = self.repo.get_nodes()
        # validate that we have some nodes indeed
        self.assertTrue(len(nodes) > 10, f"Expected at least 10 parsed nodes, but found {len(nodes)}")

        # validate that we find INamedConcepts
        named_concept_class = self.get_class("jetbrains.mps.lang.core.structure", "INamedConcept")
        named_elements = nodes.of_concept(named_concept_class)
        named_elements_with_long_names = named_elements.where(lambda named_element: len(named_element.name()) > 10)
        self.assertTrue(len(named_elements_with_long_names) > 5, f"Expected at least 5 named elements, but found {len(named_elements_with_long_names)}")

        # validate children can be found
        book_class = self.get_class("mps.cli.landefs.library.structure", "Book")
        books = nodes.of_concept(book_class)
        self.assertTrue(len(books) >= 4, f"Expected at least 4 books, but found {len(books)}")
        all_additional_authors = books.select_many(lambda it: it.authors()).where(lambda it: it is not None)
        self.assertTrue(len(all_additional_authors) >= 4, f"Expected at least 4 additional authors, but found {len(all_additional_authors)}")

        # validate references can be resolved
        persons = all_additional_authors.select(lambda it: it.person())
        self.assertTrue(len(persons) == len(all_additional_authors), f"The list of found persons must have the same size as the list of all additional authors (persons {len(persons)}, additional authors: { {len(all_additional_authors)}})")

    @staticmethod
    def get_class(module_name, class_name):
        concept_module = importlib.import_module(module_name + "." + class_name)
        concept_class = getattr(concept_module, class_name)
        return concept_class


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestLanguageStructureGenerator('test_building_languages'))
    suite.addTest(TestLanguageStructureGenerator('test_smoke_class_exist'))
    suite.addTest(TestLanguageStructureGenerator('test_using_classes'))

    runner = unittest.TextTestRunner()
    runner.run(suite)

