
import xml.etree.ElementTree as ET
from model.SModel import SModel
from model.SNode import SNode
from model.builder.SLanguageBuilder import SLanguageBuilder


class SModelBuilderFilePerRootPersistency:

    def __init__(self):
        self.index_2_concept = {}

    def build(self, path):
        model_file = path / '.model'
        model = self.extract_model_core_info(model_file)
        for file in path.iterdir():
            if file.suffix == '.mpsr':
                root_node = self.extract_root_node(file)
                model.root_nodes.append(root_node)

    def extract_root_node(self, mpsr_file):
        tree = ET.parse(mpsr_file)
        model_xml_node = tree.getroot()
        registry_xml_node = model_xml_node.find("registry")
        for language_xml_node in registry_xml_node.findall("language"):
            language_id = language_xml_node.get("id")
            language_name = language_xml_node.get("name")
            language = SLanguageBuilder.get_language(language_name, language_id)
            for concept_xml_node in language_xml_node.findall("concept"):
                concept_id = concept_xml_node.get("id")
                concept_name = concept_xml_node.get("name")
                concept = SLanguageBuilder.get_concept(language, concept_name, concept_id)
                concept_index = concept_xml_node.get("index")
                self.index_2_concept[concept_index] = concept
        return SNode("42")

    def extract_model_core_info(self, model_file):
        tree = ET.parse(model_file)
        model_xml_node = tree.getroot()
        model_name = model_xml_node.get("name")
        model_uuid = model_xml_node.get("uuid")
        model = SModel(model_name, model_uuid)
        return model
