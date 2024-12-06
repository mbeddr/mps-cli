from mpscli.model.SModule import SModule
from mpscli.model.builder.SModuleBuilder import SModuleBuilder
from mpscli.structuregen.model.SLanguageStructure import SLanguageStructure


class SLanguageStructureBuilder(SModuleBuilder):

    def build_language(self, path_to_module_file, snode_class_finder=None):
        self.build_module(path_to_module_file, snode_class_finder)

    def create_module(self, module_name, module_uuid) -> SModule:
        return SLanguageStructure(module_name, module_uuid)
