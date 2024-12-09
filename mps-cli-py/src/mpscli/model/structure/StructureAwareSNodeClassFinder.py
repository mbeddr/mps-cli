import fnmatch
import os
import inspect
import importlib.util

from mpscli.model.builder.SNodeClassFinder import SNodeClassFinder
from mpscli.model.SNode import SNode


class StructureAwareSNodeClassFinder(SNodeClassFinder):
    DEFAULT_CONCEPT_NAME = "jetbrains.mps.lang.core.structure.BaseConcept"

    def __init__(self, directory_with_node_classes):
        self.directory_with_node_classes = directory_with_node_classes
        self.concept_name_2_snode_class = {}
        self.__private_init_map()

    def __private_init_map(self):
        all_classes = self.__private_find_all_classes()
        for clazz in all_classes:
            if hasattr(clazz, 'get_concept_fqn'):
                concept_name = getattr(clazz, 'get_concept_fqn')()
                self.concept_name_2_snode_class[concept_name] = clazz
        print(f"Found  {len(self.concept_name_2_snode_class)} node classes.")

    def __private_find_all_classes(self) :
        modules = self.__private_import_all_modules()
        classes = []
        for module_name, module in modules.items():
            module_classes_tuple = inspect.getmembers(module, inspect.isclass)
            classes.extend([item[1] for item in module_classes_tuple])
        return classes

    def get_snode_class(self, concept) -> type[SNode]:
        clazz = self.concept_name_2_snode_class.get(concept.name)
        if clazz is None:
            print("No class for concept '" + concept.name + "' found. Using BaseConcept instead.")
            return self.concept_name_2_snode_class.get(self.DEFAULT_CONCEPT_NAME)
        return clazz

    def __private_find_python_modules(self):
        python_files = []
        for root, dirs, files in os.walk(self.directory_with_node_classes):
            for filename in fnmatch.filter(files, '*.py'):
                if filename != '__init__.py':  # Skip __init__.py files
                    python_files.append(os.path.join(root, filename))
        return python_files

    def __private_import_module_from_path(self, module_name, path):
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def __private_import_all_modules(self):
        modules = {}
        python_files = self.__private_find_python_modules()
        for file_path in python_files:
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            modules[module_name] = self.__private_import_module_from_path(module_name, file_path)
        return modules
