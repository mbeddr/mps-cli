import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Tuple

from mpscli.model.SSolution import SSolution
from mpscli.model.builder.SModelBuilderDefaultPersistency import (
    SModelBuilderDefaultPersistency,
)
from mpscli.model.builder.SModelBuilderFilePerRootPersistency import (
    SModelBuilderFilePerRootPersistency,
)
from mpscli.model.builder.utils.MpbBatchParser import MpbBatchParser


class SSolutionBuilder:
    # builds SSolution objects from .msd files and their associated model directories.
    # Callers that need caching or parallelism construct a MpbBatchParser with the desired settings and
    # pass it to build_all()
    def build_solution(self, path_to_msd_file: Path) -> Optional[SSolution]:
        models_dir = path_to_msd_file.parent / "models"
        if not models_dir.exists():
            print(
                f"ERROR: 'models' directory not found - no model is loaded from: {path_to_msd_file.parent}"
            )
            return None
        solutions = self.build_all([path_to_msd_file])
        return solutions[0] if solutions else None

    def build_all(
        self,
        msd_paths: List[Path],
        mpb_parser: Optional[MpbBatchParser] = None,
    ) -> List[SSolution]:
        if mpb_parser is None:
            mpb_parser = MpbBatchParser()
        solution_infos: List[Tuple[SSolution, List[Path], List[Path], List[Path]]] = []
        all_mpb_paths: List[str] = []

        for msd_path in msd_paths:
            solution = self._extract_solution_info(msd_path)
            solution.path_to_solution_file = msd_path

            models_dir = msd_path.parent / "models"
            if not models_dir.exists():
                solution_infos.append((solution, [], [], []))
                continue

            mpb, fpr, mps = self._collect_model_paths(models_dir)
            solution_infos.append((solution, mpb, fpr, mps))
            all_mpb_paths.extend(str(p) for p in mpb)

        mpb_results = mpb_parser.parse(all_mpb_paths)

        solutions = []
        for solution, mpb_paths, fpr_dirs, mps_paths in solution_infos:
            for p in mpb_paths:
                model = mpb_results.get(str(p))
                if model is not None:
                    solution.models.append(model)

            for model_path in fpr_dirs:
                try:
                    model = SModelBuilderFilePerRootPersistency().build(model_path)
                    solution.models.append(model)
                except Exception as exc:
                    import warnings

                    warnings.warn(f"Failed to parse {model_path}: {exc}")

            for model_path in mps_paths:
                try:
                    model = SModelBuilderDefaultPersistency().build(model_path)
                    solution.models.append(model)
                except Exception as exc:
                    import warnings

                    warnings.warn(f"Failed to parse {model_path}: {exc}")

            solutions.append(solution)

        return solutions

    def _collect_model_paths(
        self, models_dir: Path
    ) -> Tuple[List[Path], List[Path], List[Path]]:
        mpb, fpr, mps = [], [], []
        for p in models_dir.rglob("*"):
            if p.is_file() and p.suffix == ".mpb":
                mpb.append(p)
            elif p.is_dir() and (p / ".model").exists():
                fpr.append(p)
            elif p.is_file() and p.suffix == ".mps":
                mps.append(p)
        return mpb, fpr, mps

    def _extract_solution_info(self, solution_file: Path) -> SSolution:
        tree = ET.parse(solution_file)
        root = tree.getroot()
        return SSolution(root.get("name"), root.get("uuid"))
