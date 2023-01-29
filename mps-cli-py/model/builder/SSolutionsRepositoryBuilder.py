import datetime
import os
import sys

from pathlib import Path
from model.SRepository import SRepository
from model.builder.SLanguageBuilder import SLanguageBuilder
from model.builder.SSolutionBuilder import SSolutionBuilder

class SSolutionsRepositoryBuilder:
    repo = SRepository()

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
        stop = datetime.datetime.now()
        duration = (stop - start).microseconds / 1000
        print('duration is: ' + str(duration))
        return self.repo

    def collect_solutions_from_sources(self, path):
        for pth in Path(path).rglob('*.msd'):
            solutionBuilder = SSolutionBuilder()
            solution = solutionBuilder.build_solution(pth)
            self.repo.solutions.append(solution)
        self.repo.languages = list(SLanguageBuilder.languages.values())
