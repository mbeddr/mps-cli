
from mpscli.model.builder.SModelBuilderBase import SModelBuilderBase
import xml.etree.ElementTree as ET


class SModelBuilderFilePerRootPersistency(SModelBuilderBase):

    def build(self, path):
        model_file = path / '.model'
        tree = ET.parse(model_file)
        model_xml_node = tree.getroot()
        model = self.extract_model_core_info(model_xml_node)
        model.path_to_model_file = model_file

        for file in path.iterdir():
            if file.suffix == '.mpsr':
                root_node = self.extract_root_node(file)
                model.root_nodes.append(root_node)

        return model

    def extract_root_node(self, mpsr_file):
        tree = ET.parse(mpsr_file)
        model_xml_node = tree.getroot()
        self.extract_imports_and_registry(model_xml_node)
        root_node = model_xml_node.find("node")
        return self.extract_node(root_node)



