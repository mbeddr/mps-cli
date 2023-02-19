import os
import unittest

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder


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
