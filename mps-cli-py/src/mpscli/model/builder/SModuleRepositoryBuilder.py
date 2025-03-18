import os
import shutil
import sys
import zipfile
from pathlib import Path
from timeit import default_timer as timer

from mpscli.model.SRepository import SRepository
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.SModuleBuilder import SModuleBuilder


class SModuleRepositoryBuilder:
    def __init__(self, module_file_extension, snode_class_finder, builder_filter):
        self.repo = SRepository()
        self.module_file_extension = module_file_extension
        self.snode_class_finder = snode_class_finder
        self.builder_filter = builder_filter

    def build_from_multiple_path(self, paths):
        start = timer()
        for path in paths:
            if not os.path.exists(path):
                print("ERROR: path", path, "does not exist!")
                sys.exit(1)
            if not os.path.isdir(path):
                print("ERROR: path", path, "is not a directory!")
                sys.exit(1)

            print("building model from path:", path)
            self.collect_modules_from_sources(path)
            self.collect_modules_from_jars(path)
        self.repo.languages = list(SLanguageBuilder.languages.values())
        stop = timer()
        duration = (stop - start)
        print('duration is: ' + str(duration) + ' seconds')
        return self.repo

    def build(self, path):
        return self.build_from_multiple_path([path])

    def collect_modules_from_sources(self, path):
        for pth in Path(path).rglob('*.' + self.module_file_extension):
            module_builder = self.create_module_builder()
            module = module_builder.build_module(pth, self.repo, self.snode_class_finder)
            if module is not None:
                self.repo.solutions.append(module)

    def collect_modules_from_jars(self, path):
        for jar_path in Path(path).rglob('*.jar'):
            directory_where_to_extract = jar_path.parent / jar_path.name.replace(".", "_")
            directory_where_to_extract.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(jar_path) as jar:
                jar.extractall(directory_where_to_extract)
                print("path = ", directory_where_to_extract)
                self.collect_modules_from_sources(directory_where_to_extract)
            try:
                shutil.rmtree(directory_where_to_extract)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

    def create_module_builder(self) -> SModuleBuilder:
        pass
