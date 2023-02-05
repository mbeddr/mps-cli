import unittest
import os

from model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder
from tests.test_base import TestBase
from parameterized import parameterized


class TestLanguageExtraction(TestBase):

    @parameterized.expand(['mps_cli_lanuse_file_per_root',
                           'mps_cli_lanuse_default_persistency',
                           'mps_cli_lanuse_binary'])
    def test_languages_and_concepts(self, test_data_location):
        """
        Test the building of languages and concepts
        """
        self.doSetUp(test_data_location)
        self.assertEqual(3, len(self.repo.languages))
        mps_lang_core = self.repo.find_language_by_name("jetbrains.mps.lang.core")
        self.assertIsNotNone(mps_lang_core)
        landefs_library = self.repo.find_language_by_name("mps.cli.landefs.library")
        self.assertIsNotNone(landefs_library)
        landefs_people = self.repo.find_language_by_name("mps.cli.landefs.people")
        self.assertIsNotNone(landefs_people)

        library_concept_names = list(map(lambda c: c.name, landefs_library.concepts))
        library_concept_names.sort()
        self.assertEqual(['mps.cli.landefs.library.structure.Book',
                            'mps.cli.landefs.library.structure.Library',
                            'mps.cli.landefs.library.structure.LibraryEntityBase',
                            'mps.cli.landefs.library.structure.Magazine'], library_concept_names)
        book_concept = landefs_library.find_concept_by_name('mps.cli.landefs.library.structure.Book')
        self.assertEqual(['publicationDate'], book_concept.properties)
        self.assertEqual(['authors'], book_concept.children)



if __name__ == '__main__':
    unittest.main()