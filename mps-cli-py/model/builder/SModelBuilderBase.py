from model.SNode import SNode
from model.SNodeRef import SNodeRef


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