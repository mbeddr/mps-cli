from mpscli.structuregen.gen.ConceptDeclarationTemplateHelper import AbstractDeclarationTemplateHelper
from mpscli.structuregen.gen.StructureTemplates import get_enum_class_template


class EnumDeclarationTemplateHelper(AbstractDeclarationTemplateHelper):
    def __init__(self,  snode, snode_to_model_map):
        super().__init__(snode, snode_to_model_map)

    def get_members(self):
        members = self.snode.get_children("members")
        return [(literal.get_property("name"), literal.get_property("presentation") if literal.get_property("presentation") is not None else literal.get_property("name")) for literal in members]

    def generate_enum_class(self):
        return get_enum_class_template(self)
