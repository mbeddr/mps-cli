
import xml.etree.ElementTree as ET
from mpscli.model.builder.SModelBuilderBase import SModelBuilderBase


class SModelBuilderDefaultPersistency(SModelBuilderBase):

    def build(self, path):
        tree = ET.parse(path)
        model_xml_node = tree.getroot()
        model = self.extract_model_core_info(model_xml_node)
        model.path_to_model_file = path
        self.extract_imports_and_registry(model_xml_node)

        for node_xml_node in model_xml_node.findall("node"):
            root_node = self.extract_node(node_xml_node)
            model.root_nodes.append(root_node)

        return model
