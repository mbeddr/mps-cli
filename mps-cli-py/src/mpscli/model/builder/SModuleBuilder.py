import os
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path

from mpscli.model.SModule import SModule
from mpscli.model.builder.SModelBuilderDefaultPersistency import SModelBuilderDefaultPersistency
from mpscli.model.builder.SModelBuilderFilePerRootPersistency import SModelBuilderFilePerRootPersistency


class SModuleBuilder:

    def build_module(self, path_to_module_file, snode_class_finder=None):
        module = self.extract_module_core_info(path_to_module_file)
        path_to_module_dir = path_to_module_file.parent
        module.path_to_module_file = path_to_module_file
        print("building from:", path_to_module_dir)
        path_to_models_dir = path_to_module_dir / module.module_model_folder
        if not os.path.exists(path_to_models_dir):
            print(f"ERROR: Models directory '{module.path_to_module_file}' not found! No model is loaded from path: " + str(path_to_module_dir))
            return None
        path_to_models_dir = self.skip_empty_dirs(path_to_models_dir)
        paths_to_models_dir = deque([path_to_models_dir])
        while paths_to_models_dir:
            model_dir = paths_to_models_dir.popleft()
            for path_to_model in model_dir.iterdir():
                if path_to_model.is_dir():
                    if self.is_file_per_root_persistency_dir(path_to_model):
                        builder = SModelBuilderFilePerRootPersistency(snode_class_finder)
                    else:
                        paths_to_models_dir.append(path_to_model)
                        continue
                else:
                    builder = SModelBuilderDefaultPersistency(snode_class_finder)
                model = builder.build(path_to_model)
                if model is not None:
                    module.models.append(model)

        return module

    def extract_module_core_info(self, module_file):
        tree = ET.parse(module_file)
        module_xml_node = tree.getroot()
        module_name = module_xml_node.get(self.tag_for_name_attribute())
        module_uuid = module_xml_node.get("uuid")
        source_root = module_xml_node.find('.//sourceRoot')
        if source_root is not None:
            module_model_folder = source_root.get("location")
        else:
            module_model_folder = "models"
        module = self.create_module(module_name, module_uuid, module_model_folder)
        return module

    def tag_for_name_attribute(self):
        return "name"

    def create_module(self, module_name, module_uuid, module_model_folder) -> SModule:
        pass

    def is_file_per_root_persistency_dir(self, path_to_model):
        # the path/folder contains a .model file --> model dir for file per root found
        return '.model' in os.listdir(path_to_model)

    def skip_empty_dirs(self, path_to_models_dir):
        """
        In some cases - especially for languages - the top level path to model dir provided is empty as the models are
        stored in a folder hierarchy that represents the fqn of the module. These folders need to be skipped so that the next folder either
        contains the models directly (if default persistencu is used) or contains the .model file (in case of file per root persistencu)

        :return: the actual path to dir of the models
        """
        entries = os.listdir(path_to_models_dir)
        if len(entries) != 1:
            # more than one entry --> model dir found
            return path_to_models_dir
        subfolders = [entry for entry in entries if os.path.isdir(os.path.join(path_to_models_dir, entry))]
        if len(subfolders) != 1:
            # more than one sub folder --> model dir found
            return path_to_models_dir
        path_to_subfolder = os.path.join(path_to_models_dir, subfolders[0])
        if self.is_file_per_root_persistency_dir(path_to_subfolder):
            return path_to_models_dir
        # the folder needs to be skipped
        return self.skip_empty_dirs(Path(path_to_subfolder))
