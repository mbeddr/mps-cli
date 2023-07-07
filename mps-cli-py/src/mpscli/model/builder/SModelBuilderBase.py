from mpscli.model.SNodeRef import SNodeRef
from mpscli.model.SModel import SModel
from mpscli.model.SNode import SNode
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder


class SModelBuilderBase:

    def __init__(self):
        self.index_2_concept = {}
        self.index_2_property = {}
        self.index_2_child_role_in_parent = {}
        self.index_2_reference_role = {}
        self.index_2_imported_model_uuid = {}

    def extract_node(self, node_xml):
        root_node_id = node_xml.get("id")
        root_node_concept = self.index_2_concept[node_xml.get("concept")]
        child_role_index = node_xml.get("role")
        if child_role_index is None:
            child_role = None
        else:
            child_role = self.index_2_child_role_in_parent[child_role_index]
        s_node = SNode(root_node_id, root_node_concept, child_role)
        for property_xml_node in node_xml.findall("property"):
            property_role = property_xml_node.get("role")
            property_value = property_xml_node.get("value")
            property_name = self.index_2_property[property_role]
            s_node.properties[property_name] = property_value
        for ref_xml_node in node_xml.findall("ref"):
            ref_role = ref_xml_node.get("role")
            ref_to = ref_xml_node.get("to")
            ref_name = self.index_2_reference_role[ref_role]
            ref_model_index = ref_to[0 : ref_to.find(":")]
            ref_node_uuid = ref_to[ref_to.find(":") + 1 : len(ref_to)]
            s_node.references[ref_name] = SNodeRef(self.index_2_imported_model_uuid[ref_model_index], ref_node_uuid)
        for child_node_xml in node_xml.findall("node"):
            child_node = self.extract_node(child_node_xml)
            s_node.children.append(child_node)

        return s_node

    def extract_model_core_info(self, model_xml_node):
        model_ref = model_xml_node.get("ref")
        model_name = model_ref[model_ref.find("(") + 1 : len(model_ref) - 1]
        model_uuid = model_ref[0 : model_ref.find("(")]
        model = SModel(model_name, model_uuid)
        return model

    def extract_imports_and_registry(self, model_xml_node):
        imports_xml_node = model_xml_node.find("imports")
        for import_xml_node in imports_xml_node.findall("import"):
            import_index = import_xml_node.get("index")
            imported_model_ref = import_xml_node.get("ref")
            imported_model_uuid = imported_model_ref[0: imported_model_ref.find("(")]
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
