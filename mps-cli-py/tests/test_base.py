import os
import unittest

from model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder


class TestBase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(TestBase, self).__init__(methodName)

    def setUp(self):
        """
        Builds the object model based on the file-per-root MPS models
        """
        builder = SSolutionsRepositoryBuilder()
        path = os.path.abspath('..\\mps_test_projects\\mps_cli_lanuse_file_per_root')
        self.repo = builder.build(path)