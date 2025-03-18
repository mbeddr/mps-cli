from mpscli.model.builder.SModuleBuilder import SModuleBuilder
from mpscli.model.builder.SModuleRepositoryBuilder import SModuleRepositoryBuilder
from mpscli.structuregen.model.builder.SLanguageStructureBuilder import SLanguageStructureBuilder


class SLanguageStructureRepositoryBuilder(SModuleRepositoryBuilder):

    def __init__(self, snode_class_finder=None, builder_filter=None):
        super().__init__("mpl", snode_class_finder, builder_filter)

    def create_module_builder(self) -> SModuleBuilder:
        return SLanguageStructureBuilder(self.builder_filter)
