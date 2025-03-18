from mpscli.model.builder.SModuleBuilder import SModuleBuilder
from mpscli.model.builder.SModuleRepositoryBuilder import SModuleRepositoryBuilder
from mpscli.model.builder.SSolutionBuilder import SSolutionBuilder


class SSolutionsRepositoryBuilder(SModuleRepositoryBuilder):

    def __init__(self, snode_class_finder=None, builder_filter=None):
        super().__init__("msd", snode_class_finder, builder_filter)

    def create_module_builder(self) -> SModuleBuilder:
        return SSolutionBuilder(self.builder_filter)
