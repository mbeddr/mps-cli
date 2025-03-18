from mpscli.model.SModule import SModule
from mpscli.model.builder.SModuleBuilder import SModuleBuilder
from mpscli.structuregen.model.SLanguageStructure import SLanguageStructure


class SLanguageStructureBuilder(SModuleBuilder):

    def build_language(self, path_to_module_file, repo = None, snode_class_finder=None):
        self.build_module(path_to_module_file, repo, snode_class_finder)

    def create_module(self, module_name, module_uuid, module_model_folder) -> SModule:
        return SLanguageStructure(module_name, module_uuid, module_model_folder)

    def tag_for_name_attribute(self):
        return "namespace"
