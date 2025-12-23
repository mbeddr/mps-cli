
from mpscli.model.builder.SModelBuilderBinaryPersistency import SModelBuilderBinaryPersistency
from tests.test_base import TestBase


class TestBinaryPersistencyLowLevelAccess(TestBase):

    def testReadModelId(self):
        path_to_model = "../mps_test_projects/mps_cli_binary_persistency_generated_low_level_access_test_data/mps.cli.lanuse.library_top.binary_persistency.authors_top.mpb"
        with open(path_to_model, mode='rb') as file: 
            fileContent = file.read()
            binaryPersistencyReader = SModelBuilderBinaryPersistency()
            modelId = binaryPersistencyReader.readModelId(fileContent, 9)

            self.assertEqual('cf91f372-8bfd-44b8-8e34-024eb23e64a8', modelId)
        # Test reading model reference
        pass

