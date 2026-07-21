# mpscli/model/builder/utils/DiskModelLoader.py
#
# Builds SSolution objects from disk .msd filess
# For MPB - parsed serially via MpbBatchParser (workers=1 avoids GIL contention with load_sync ThreadPool)..
# For FPR/MPS: preread bytes supplied from a background IO thread (preread_disk_bytes) that runs during phase2
# Parsing uses a ProcessPool so each worker gets a full cpu core and there is no GIL contention and the 
# SLanguageBuilder is fully locked so concurrent mutations from workers are safe via lang_pairs.
# On warm runs the ParseCache disk cache supplies models directly so parse_tasks is empty..
# On cold runs with workers=1 parsing runs serially using 1-2 CPU cores which would be concurrent with phase4 
# ProcessPool which uses the remaining cores.

import logging
import threading
import warnings
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Tuple

from mpscli.model.SSolution import SSolution
from mpscli.model.builder.utils.MpbBatchParser import MpbBatchParser

_log = logging.getLogger(__name__)

# minimum number of tasks before spawning a ProcessPool for phase3
_FPR_POOL_THRESHOLD = 8


def preread_disk_bytes(msd_paths: List[Path], io_workers: int = 32) -> dict:
    # preread all fpr .model/.mpsr and MPS bytes and this is pure I/O and no parsing..
    # This is called from a background thread that starts before phase2
    tasks = []
    for idx, msd_path in enumerate(msd_paths):
        models_dir = msd_path.parent / "models"
        if not models_dir.exists():
            continue
        _, fpr, mps = _collect_model_paths(models_dir)
        for fp in fpr:
            tasks.append(("fpr", idx, fp))
        for mp in mps:
            tasks.append(("mps", idx, mp))

    if not tasks:
        return {}

    preread: dict = {}
    lock = threading.Lock()

    def read_task(task):
        kind, idx, path = task
        try:
            if kind == "fpr":
                model_bytes = (path / ".model").read_bytes()
                mpsr_data = [
                    (str(f), f.read_bytes()) for f in sorted(path.glob("*.mpsr"))
                ]
                with lock:
                    preread[(kind, idx, path)] = (model_bytes, mpsr_data)
            else:
                with lock:
                    preread[(kind, idx, path)] = path.read_bytes()
        except Exception as exc:
            warnings.warn(f"Failed to preread {path}: {exc}")

    with ThreadPoolExecutor(max_workers=min(len(tasks), io_workers)) as pool:
        list(pool.map(read_task, tasks))

    return preread


def load_disk_solutions(
    msd_paths: List[Path],
    mpb_parser: Optional[MpbBatchParser] = None,
    preread_bytes: Optional[dict] = None,
    cache_load_fn=None,
    cache_save_fn=None,
    workers: int = 1,
    parse_cache=None,
    msd_stats=None,
) -> List[SSolution]:
    if mpb_parser is None:
        mpb_parser = MpbBatchParser()

    solution_infos: List[Tuple[SSolution, List[Path], List[Path], List[Path]]] = []
    all_mpb_paths: List[str] = []

    for msd_path in msd_paths:
        solution = _extract_solution_info(msd_path)
        solution.path_to_solution_file = msd_path
        models_dir = msd_path.parent / "models"
        if not models_dir.exists():
            solution_infos.append((solution, [], [], []))
            continue
        mpb, fpr, mps = _collect_model_paths(models_dir)
        solution_infos.append((solution, mpb, fpr, mps))
        all_mpb_paths.extend(str(p) for p in mpb)

    mpb_results = mpb_parser.parse(all_mpb_paths)

    # separate MPB assignment and cache hits from FPR/MPS parse tasks so each task would 
    # be (kind, sol_idx, path, data_or_bytes, mpsr_data_or_none, cache_key)
    parse_tasks = []
    disk_cache_pending: dict = {}

    solutions = []
    for idx, (solution, mpb_paths, fpr_dirs, mps_paths) in enumerate(solution_infos):
        msd_path_str = str(solution.path_to_solution_file)
        for p in mpb_paths:
            model = mpb_results.get(str(p))
            if model is not None:
                solution.models.append(model)

        # warm path - check ParseCache disk cache for this whole solutions FPR/MPS modelss
        disk_cached = (
            parse_cache.get_disk(msd_path_str) if parse_cache is not None else None
        )
        if disk_cached is not None:
            for model in disk_cached.values():
                solution.models.append(model)
            solutions.append(solution)
            continue

        # mark this solution for disk cache save after parsing
        if parse_cache is not None:
            disk_cache_pending[msd_path_str] = idx

        for fp in fpr_dirs:
            model_file = fp / ".model"
            if cache_load_fn is not None:
                model = cache_load_fn(model_file)
                if model is not None:
                    solution.models.append(model)
                    continue
            key = ("fpr", idx, fp)
            if preread_bytes is not None and key in preread_bytes:
                model_bytes, mpsr_data = preread_bytes[key]
            else:
                try:
                    model_bytes = (fp / ".model").read_bytes()
                    mpsr_data = [
                        (str(f), f.read_bytes()) for f in sorted(fp.glob("*.mpsr"))
                    ]
                except Exception as exc:
                    warnings.warn(f"Failed to read {fp}: {exc}")
                    continue
            parse_tasks.append(("fpr", idx, fp, model_bytes, mpsr_data, model_file))

        for mp in mps_paths:
            if cache_load_fn is not None:
                model = cache_load_fn(mp)
                if model is not None:
                    solution.models.append(model)
                    continue
            key = ("mps", idx, mp)
            if preread_bytes is not None and key in preread_bytes:
                data = preread_bytes[key]
            else:
                try:
                    data = mp.read_bytes()
                except Exception as exc:
                    warnings.warn(f"Failed to read {mp}: {exc}")
                    continue
            parse_tasks.append(("mps", idx, mp, data, None, mp))

        solutions.append(solution)

    if not parse_tasks:
        return solutions

    from mpscli.model.builder.utils.JarModelLoader import (
        _parse_fpr_bytes_worker,
        _parse_mps_bytes_worker,
    )
    from mpscli.model.builder.utils.MpbBatchParser import _register_lang_pairs

    fpr_count = sum(1 for t in parse_tasks if t[0] == "fpr")
    mps_count = sum(1 for t in parse_tasks if t[0] == "mps")
    _log.info(
        "[diag] disk parse_tasks: %d tasks (%d fpr, %d mps), %d solutions, workers=%d",
        len(parse_tasks),
        fpr_count,
        mps_count,
        len(solutions),
        workers,
    )

    # accumulate lang_pairs per msd solution so they can be stored in cache and
    # re-registered on warm loads and this fixes warm language count bug..
    msd_lang_pairs: dict = {}

    def _accumulate_lang_pairs(msd_path_str: str, lang_pairs: list) -> None:
        if not lang_pairs:
            return
        existing = msd_lang_pairs.get(msd_path_str, [])
        seen = {(n, u) for n, u in existing}
        for lp in lang_pairs:
            if lp not in seen:
                existing.append(lp)
                seen.add(lp)
        msd_lang_pairs[msd_path_str] = existing

    # build reverse mapping from sol_idx to msd_path_str forr lang_pairs accumulation
    idx_to_msd = {v: k for k, v in disk_cache_pending.items()}

    def _handle_result(model, lang_pairs, kind, sol_idx, path):
        if kind == "fpr":
            model.path_to_model_file = path / ".model"
        else:
            model.path_to_model_file = path
        if lang_pairs:
            _register_lang_pairs(lang_pairs)
            msd_path_str = idx_to_msd.get(sol_idx)
            if msd_path_str:
                _accumulate_lang_pairs(msd_path_str, lang_pairs)
        solutions[sol_idx].models.append(model)

    def _run_serial():
        # serial path - called from disk-build thread (workers= 1) which runs concurrently with phase4 
        # ProcessPool and uses only 1-2 CPU cores I guess so phase4 gets the rest..
        for task in parse_tasks:
            kind, sol_idx, path, data_or_bytes, mpsr_data, cache_key = task
            try:
                if kind == "fpr":
                    model, lang_pairs = _parse_fpr_bytes_worker(
                        data_or_bytes, mpsr_data
                    )
                else:
                    model, lang_pairs = _parse_mps_bytes_worker(data_or_bytes)
                _handle_result(model, lang_pairs, kind, sol_idx, path)
            except Exception as exc:
                warnings.warn(f"Failed to parse {path}: {exc}")

    if len(parse_tasks) < _FPR_POOL_THRESHOLD or workers <= 1:
        _run_serial()
    else:
        # ProcessPool path - only reached when workers > 1 which currently only happens in tests or future 
        # callers and the disk-build thread always passes workers=1
        future_to_task = {}
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for task in parse_tasks:
                kind, sol_idx, path, data_or_bytes, mpsr_data, cache_key = task
                if kind == "fpr":
                    f = pool.submit(_parse_fpr_bytes_worker, data_or_bytes, mpsr_data)
                else:
                    f = pool.submit(_parse_mps_bytes_worker, data_or_bytes)
                future_to_task[f] = task

            for future in as_completed(future_to_task):
                kind, sol_idx, path, _, _, _ = future_to_task[future]
                try:
                    model, lang_pairs = future.result()
                    _handle_result(model, lang_pairs, kind, sol_idx, path)
                except Exception as exc:
                    warnings.warn(f"Failed to parse {path}: {exc}")

    # save newly parsed FPR/MPS models to disk cache per solution including lang_pairs so warm loads 
    # can re-register registry-only languages correctly...
    if parse_cache is not None and disk_cache_pending:
        disk_cache_map = {}
        for msd_path_str, sol_idx in disk_cache_pending.items():
            sol = solutions[sol_idx]
            fpr_mps_models = {
                str(m.path_to_model_file): m for m in sol.models if m.path_to_model_file
            }
            if fpr_mps_models:
                disk_cache_map[msd_path_str] = fpr_mps_models
        if disk_cache_map:
            parse_cache.put_disk_many(
                disk_cache_map,
                msd_stats,
                lang_pairs_map=msd_lang_pairs if msd_lang_pairs else None,
            )

    return solutions


def _parse_fpr_bytes(model_bytes: bytes, mpsr_data: list, fpr_path: Path = None):
    # parse FPR from pre-read bytes in-process so basically no file I/O.. This is called from disk_thread so basically
    # no shared mutable state between callers.
    # fpr_path is the fpr directory used to set model.path_to_model_file so it matches what 
    # SModelBuilderFilePerRootPersistency.build() would actually set..
    try:
        from lxml import etree as ET
    except ImportError:
        import xml.etree.ElementTree as ET
    from mpscli.model.builder.SModelBuilderFilePerRootPersistency import (
        SModelBuilderFilePerRootPersistency,
    )

    builder = SModelBuilderFilePerRootPersistency()
    model_xml = ET.fromstring(model_bytes)
    model = builder.extract_model_core_info(model_xml)
    if fpr_path is not None:
        model.path_to_model_file = fpr_path / ".model"
    for _name, mpsr_bytes in mpsr_data:
        try:
            mpsr_xml = ET.fromstring(mpsr_bytes)
            builder.extract_registry(mpsr_xml)
            root = mpsr_xml.find("node")
            if root is not None:
                root_node = builder.extract_node(model, root, None)
                model.root_nodes.append(root_node)
        except Exception:
            pass
    return model


def _parse_mps_bytes(data: bytes, mps_path: Path = None):
    # parse MPS from preread bytes in-process so basically no file I/O. Also, mps_path is the source .mps file used
    # to set model.path_to_model_file so it matches what SModelBuilderDefaultPersistency.build() would set
    try:
        from lxml import etree as ET
    except ImportError:
        import xml.etree.ElementTree as ET
    from mpscli.model.builder.SModelBuilderDefaultPersistency import (
        SModelBuilderDefaultPersistency,
    )

    builder = SModelBuilderDefaultPersistency()
    model_xml = ET.fromstring(data)
    model = builder.extract_model_core_info(model_xml)
    if mps_path is not None:
        model.path_to_model_file = mps_path
    builder.extract_registry(model_xml)
    for node_xml in model_xml.findall("node"):
        root_node = builder.extract_node(model, node_xml, None)
        model.root_nodes.append(root_node)
    return model


def _collect_model_paths(
    models_dir: Path,
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


def _extract_solution_info(solution_file: Path) -> SSolution:
    tree = ET.parse(solution_file)
    root = tree.getroot()
    return SSolution(root.get("name"), root.get("uuid"))


def parse_fpr(model_path: Path, cache_load_fn=None, cache_save_fn=None):
    # parse one FPR model directory with optional ModelCache integration. This is used by SSolutionBuilder
    # for disk-resident FPR models
    model_file = model_path / ".model"
    if cache_load_fn is not None:
        cached = cache_load_fn(model_file)
        if cached is not None:
            return cached
    model_bytes = model_file.read_bytes()
    mpsr_data = [(str(f), f.read_bytes()) for f in sorted(model_path.glob("*.mpsr"))]
    model = _parse_fpr_bytes(model_bytes, mpsr_data, fpr_path=model_path)
    if model is not None and cache_save_fn is not None:
        cache_save_fn(model_file, model)
    return model


def parse_mps(model_path: Path, cache_load_fn=None, cache_save_fn=None):
    # parse one .mps model file with optional ModelCache integration..
    # This is used by SSolutionBuilder for disk-resident MPS models
    if cache_load_fn is not None:
        cached = cache_load_fn(model_path)
        if cached is not None:
            return cached
    model = _parse_mps_bytes(model_path.read_bytes(), mps_path=model_path)
    if model is not None and cache_save_fn is not None:
        cache_save_fn(model_path, model)
    return model
