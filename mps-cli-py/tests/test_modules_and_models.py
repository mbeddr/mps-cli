import unittest
import os

from model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder
from tests.test_base import TestBase


class TestModulesAndModels(TestBase):

    def test_build_modules_and_models(self):
        """
        Test the building of modules and models
        """
        self.assertEqual(2, len(self.repo.solutions))

        library_second = self.repo.find_solution_by_name('mps.cli.lanuse.library_second')
        self.assertNotEqual(None, library_second)

        library_top = self.repo.find_solution_by_name('mps.cli.lanuse.library_top')
        self.assertNotEqual(None, library_top)

        library_second_models_names = list(map(lambda mod : mod.name, library_second.models))
        library_second_models_names.sort()
        self.assertEqual(['mps.cli.lanuse.library_second.library_top'], library_second_models_names)

        library_top_authors_top = self.repo.find_model_by_name('mps.cli.lanuse.library_top.authors_top')
        self.assertNotEqual(None, library_top_authors_top)
        self.assertEqual('mps.cli.lanuse.library_top.authors_top', library_top_authors_top.name)
        self.assertEqual('r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed', library_top_authors_top.uuid)

if __name__ == '__main__':
    unittest.main()