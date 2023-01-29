
import xml.etree.ElementTree as ET
from model.SModel import SModel
from model.SNode import SNode
from model.builder.SLanguageBuilder import SLanguageBuilder
from model.builder.SModelBuilderBase import SModelBuilderBase


class SModelBuilderFilePerRootPersistency(SModelBuilderBase):

    def build(self, path):
        model_file = path / '.model'
        model = self.extract_model_core_info(model_file)
        for file in path.iterdir():
            if file.suffix == '.mpsr':
                root_node = self.extract_root_node(file)
                model.root_nodes.append(root_node)
        return model

    def extract_root_node(self, mpsr_file):
        tree = ET.parse(mpsr_file)
        model_xml_node = tree.getroot()

        imports_xml_node = model_xml_node.find("imports")
        for import_xml_node in imports_xml_node.findall("import"):
            import_index = import_xml_node.get("index")
            imported_model_ref = import_xml_node.get("ref")
            imported_model_uuid = imported_model_ref[0 : imported_model_ref.find("(")]
            self.index_2_imported_model_uuid[import_index] = imported_model_uuid

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
                for property_xml_node in concept_xml_node.findall("property"):
                    property_name = property_xml_node.get("name")
                    property_index = property_xml_node.get("index")
                    node_property = SLanguageBuilder.get_property(concept, property_name)
                    self.index_2_property[property_index] = node_property
                for child_xml_node in concept_xml_node.findall("child"):
                    child_name = child_xml_node.get("name")
                    child_index = child_xml_node.get("index")
                    child = SLanguageBuilder.get_child(concept, child_name)
                    self.index_2_child_role_in_parent[child_index] = child
                for reference_xml_node in concept_xml_node.findall("reference"):
                    reference_name = reference_xml_node.get("name")
                    reference_index = reference_xml_node.get("index")
                    reference = SLanguageBuilder.get_reference(concept, reference_name)
                    self.index_2_reference_role[reference_index] = reference

        root_node = model_xml_node.find("node")
        return self.extract_node(root_node)

    def extract_model_core_info(self, model_file):
        tree = ET.parse(model_file)
        model_xml_node = tree.getroot()
        model_ref = model_xml_node.get("ref")
        model_name = model_ref[model_ref.find("(") + 1 : len(model_ref) - 1]
        model_uuid = model_ref[0 : model_ref.find("(")]
        model = SModel(model_name, model_uuid)
        return model
