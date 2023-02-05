import os
import unittest

from model.builder.SLanguageBuilder import SLanguageBuilder
from model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder


class TestBase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(TestBase, self).__init__(methodName)

    def doSetUp(self, test_data_location):
        """
        Builds the object model based on MPS models
        """
        SLanguageBuilder.languages = {}
        builder = SSolutionsRepositoryBuilder()
        test_data_location = '../mps_test_projects/' + test_data_location
        print("test data location ", test_data_location)
        path = os.path.abspath(test_data_location)
        self.repo = builder.build(path)
