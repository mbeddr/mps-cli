from timeit import default_timer as timer
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

    def build(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        elif not isinstance(paths, list):
            print("ERROR: paths should be either a string or a list of strings!")
            sys.exit(1)

        start = timer()
        for path in paths:
            if not os.path.exists(path):
                print("ERROR: path", path, "does not exist!")
                continue
            if not os.path.isdir(path):
                print("ERROR: path", path, "is not a directory!")
                continue

            print("building model from path:", path)
            self.collect_solutions_from_sources(path)
            self.collect_solutions_from_jars(path)
        self.repo.languages = list(SLanguageBuilder.languages.values())
        stop = timer()
        duration = (stop - start)
        print('duration for parsing modules: ' + str(duration) + ' seconds')
        return self.repo

    def collect_solutions_from_sources(self, path):
        for pth in Path(path).rglob('*.msd'):
            solutionBuilder = SSolutionBuilder()
            solution = solutionBuilder.build_solution(pth)
            if solution is not None:
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
