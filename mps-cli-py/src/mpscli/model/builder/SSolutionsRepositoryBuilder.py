import datetime
import os
import sys
import zipfile
import shutil

from pathlib import Path
from mpscli.model.SRepository import SRepository
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.SSolutionBuilder import SSolutionBuilder

class SSolutionsRepositoryBuilder:

    def __init__(self):
        self.repo = SRepository()

    def build(self, path):
        if not os.path.exists(path):
            print("ERROR: path", path, "does not exist!")
            sys.exit(1)
        if not os.path.isdir(path):
            print("ERROR: path", path, "is not a directory!")
            sys.exit(1)

        print("building model from path:", path)
        start = datetime.datetime.now()
        self.collect_solutions_from_sources(path)
        self.collect_solutions_from_jars(path)
        self.repo.languages = list(SLanguageBuilder.languages.values())
        stop = datetime.datetime.now()
        duration = (stop - start).microseconds / 1000
        print('duration is: ' + str(duration))
        return self.repo

    def collect_solutions_from_sources(self, path):
        for pth in Path(path).rglob('*.msd'):
            solutionBuilder = SSolutionBuilder()
            solution = solutionBuilder.build_solution(pth)
            self.repo.solutions.append(solution)

    def collect_solutions_from_jars(self, path):
        for jar_path in Path(path).rglob('*.jar'):
            directory_where_to_extract = jar_path.parent / jar_path.name.replace(".", "_")
            directory_where_to_extract.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(jar_path) as jar:
                jar.extractall(directory_where_to_extract)
                print("path = ", directory_where_to_extract)
                self.collect_solutions_from_sources(directory_where_to_extract)
            try:
                shutil.rmtree(directory_where_to_extract)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
