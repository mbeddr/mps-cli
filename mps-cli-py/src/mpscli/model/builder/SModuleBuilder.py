import os
import xml.etree.ElementTree as ET

from mpscli.model.SModule import SModule
from mpscli.model.SSolution import SSolution
from mpscli.model.builder.SModelBuilderDefaultPersistency import SModelBuilderDefaultPersistency
from mpscli.model.builder.SModelBuilderFilePerRootPersistency import SModelBuilderFilePerRootPersistency


class SModuleBuilder:

    def build_module(self, path_to_module_file, snode_class_finder=None):
        module = self.extract_module_core_info(path_to_module_file)
        path_to_module_dir = path_to_module_file.parent
        module.path_to_module_file = path_to_module_file
        print("building from:", path_to_module_dir)
        path_to_models_dir = path_to_module_dir / 'models'
        if not os.path.exists(path_to_models_dir):
            print("ERROR: 'models' directory not found! No model is loaded from path: " + str(path_to_module_dir))
            return None

        for path_to_model in path_to_models_dir.iterdir():
            if path_to_model.is_dir():
                builder = SModelBuilderFilePerRootPersistency(snode_class_finder)
            else:
                builder = SModelBuilderDefaultPersistency(snode_class_finder)
            model = builder.build(path_to_model)
            module.models.append(model)

        return module

    def extract_module_core_info(self, module_file):
        tree = ET.parse(module_file)
        module_xml_node = tree.getroot()
        module_name = module_xml_node.get("name")
        module_uuid = module_xml_node.get("uuid")
        module = self.create_module(module_name, module_uuid)
        return module

    def create_module(self, module_name, module_uuid) -> SModule:
        pass
