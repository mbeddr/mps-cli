import os
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Tuple

from mpscli.model.SSolution import SSolution
from mpscli.model.builder.SModelBuilderDefaultPersistency import (
    SModelBuilderDefaultPersistency,
)
from mpscli.model.builder.SModelBuilderFilePerRootPersistency import (
    SModelBuilderFilePerRootPersistency,
)
from mpscli.model.builder.SModelBuilderBinaryPersistency import (
    SModelBuilderBinaryPersistency,
)


def _parse_mpb(path_str: str):
    """Parse one .mpb file in a worker process. Returns SModel."""
    builder = SModelBuilderBinaryPersistency()
    return builder.build(path_str)


class SSolutionBuilder:
    MPB_WORKERS: Optional[int] = None
    MPB_PARALLEL_THRESHOLD: int = 4
    USE_CACHE: bool = False
    CACHE_LOAD_FN = None
    CACHE_SAVE_FN = None
    # set true to print a one-line status for each .mpb file as it completes
    SHOW_PROGRESS: bool = False

    def build_solution(self, path_to_msd_file: Path) -> Optional[SSolution]:
        # build a single solution (opens its own worker pool for .mpb files)
        solutions = self.build_all([path_to_msd_file])
        return solutions[0] if solutions else None

    def build_all(self, msd_paths: List[Path]) -> List[SSolution]:
        # build multiple solutions sharing only one process pool for all .mpb files.
        # phase 1: collect all paths (but no parsing yet)
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

        # phase 2: parse all the .mpb files in one parallel batch
        mpb_results: dict[str, object] = {}

        if all_mpb_paths:
            workers = self.MPB_WORKERS or min(os.cpu_count() or 4, 16)
            total = len(all_mpb_paths)

            # Only use a process pool when the batch is large enough to justify the spawn overhead
            use_pool = workers > 1 and len(all_mpb_paths) > self.MPB_PARALLEL_THRESHOLD

            if not use_pool:
                for done, ps in enumerate(all_mpb_paths, 1):
                    try:
                        cached = (
                            self.CACHE_LOAD_FN(Path(ps))
                            if self.USE_CACHE and self.CACHE_LOAD_FN
                            else None
                        )
                        if cached is not None:
                            mpb_results[ps] = cached
                        else:
                            model = _parse_mpb(ps)
                            mpb_results[ps] = model
                            if (
                                self.USE_CACHE
                                and self.CACHE_SAVE_FN
                                and model is not None
                            ):
                                self.CACHE_SAVE_FN(Path(ps), model)
                        if self.SHOW_PROGRESS:
                            print(f"[{done}/{total}] OK  {os.path.basename(ps)}")
                    except Exception as exc:
                        import warnings

                        warnings.warn(f"Failed to parse {ps}: {exc}")
                        mpb_results[ps] = None
                        if self.SHOW_PROGRESS:
                            print(f"[{done}/{total}] ERR {os.path.basename(ps)}")
            else:
                # for large batches firsst check cache first, only after that submit uncached to pool
                uncached_paths = []
                for ps in all_mpb_paths:
                    cached = (
                        self.CACHE_LOAD_FN(Path(ps))
                        if self.USE_CACHE and self.CACHE_LOAD_FN
                        else None
                    )
                    if cached is not None:
                        mpb_results[ps] = cached
                    else:
                        uncached_paths.append(ps)

                if uncached_paths:
                    import multiprocessing

                    # maybe much safer
                    multiprocessing.freeze_support()
                    done = len(all_mpb_paths) - len(
                        uncached_paths
                    )  # cached files already counted
                    with ProcessPoolExecutor(max_workers=workers) as pool:
                        future_to_path = {
                            pool.submit(_parse_mpb, ps): ps for ps in uncached_paths
                        }
                        for future in as_completed(future_to_path):
                            ps = future_to_path[future]
                            done += 1
                            try:
                                model = future.result()
                                mpb_results[ps] = model
                                if (
                                    self.USE_CACHE
                                    and self.CACHE_SAVE_FN
                                    and model is not None
                                ):
                                    self.CACHE_SAVE_FN(Path(ps), model)
                                if self.SHOW_PROGRESS:
                                    print(
                                        f"[{done}/{total}] OK  {os.path.basename(ps)}"
                                    )
                            except Exception as exc:
                                import warnings

                                warnings.warn(f"Failed to parse {ps}: {exc}")
                                mpb_results[ps] = None
                                if self.SHOW_PROGRESS:
                                    print(
                                        f"[{done}/{total}] ERR {os.path.basename(ps)}"
                                    )

        # phase 3: assemble solutions
        solutions = []
        for solution, mpb_paths, fpr_dirs, mps_paths in solution_infos:
            # .mpb models — already parsed
            for p in mpb_paths:
                model = mpb_results.get(str(p))
                if model is not None:
                    solution.models.append(model)

            # file-per-root (.model dirs)
            for model_path in fpr_dirs:
                try:
                    model = SModelBuilderFilePerRootPersistency().build(model_path)
                    solution.models.append(model)
                except Exception as exc:
                    import warnings

                    warnings.warn(f"Failed to parse {model_path}: {exc}")

            # xml .mps files
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

    def build_solution_from_msd(self, path_to_msd_file: Path) -> Optional[SSolution]:
        return self.build_solution(path_to_msd_file)

    def extract_solution_core_info(self, solution_file: Path) -> SSolution:
        return self._extract_solution_info(solution_file)
