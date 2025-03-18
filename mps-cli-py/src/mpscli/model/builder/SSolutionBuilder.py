from mpscli.model.SModule import SModule
from mpscli.model.SSolution import SSolution
from mpscli.model.builder.SModuleBuilder import SModuleBuilder


class SSolutionBuilder(SModuleBuilder):

    def build_solution(self, path_to_msd_file, repo=None, snode_class_finder=None):
        return self.build_module(path_to_msd_file, repo, snode_class_finder)

    def create_module(self, module_name, module_uuid, module_model_folder) -> SModule:
        return SSolution(module_name, module_uuid, module_model_folder)
