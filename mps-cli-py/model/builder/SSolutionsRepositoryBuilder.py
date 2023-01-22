
from pathlib import Path
from model.SRepository import SRepository
from model.builder.SSolutionBuilder import SSolutionBuilder
import datetime


class SSolutionsRepositoryBuilder:
    repo = SRepository()

    def build(self, path):
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
