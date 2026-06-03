# mpscli/model/builder/utils/DiskModelLoader.py
#
# Builds SSolution objects from disk .msd files.
# MPB: parsed serially via MpbBatchParser (workers=1 avoids GIL contention with load_sync's ThreadPool).
# FPR/MPS: preread bytes supplied from a background I/O thread (preread_disk_bytes) that runs during phase2.
# disk_thread then parses from memory with mostly zero file I/O which eliminates competition with phase4
# ProcessPool workers.
# And on warm runs the ModelCache supplies models directly so basicallyy preread bytes are unused.

import threading
import warnings
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional, Tuple

from mpscli.model.SSolution import SSolution
from mpscli.model.builder.utils.MpbBatchParser import MpbBatchParser


def preread_disk_bytes(msd_paths: List[Path], io_workers: int = 32) -> dict:
    # preread all FPR .model/.mpsr and MPS bytes and this is pure I/O and no parsing..
    # This is called from a background thread that starts before phase2
    # key: ('fpr', idx, path) -> (model_bytes, [(name, mpsr_bytes), ...])
    #      ('mps', idx, path) -> data_bytes
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

    solutions = []
    for idx, (solution, mpb_paths, fpr_dirs, mps_paths) in enumerate(solution_infos):
        for p in mpb_paths:
            model = mpb_results.get(str(p))
            if model is not None:
                solution.models.append(model)

        for fp in fpr_dirs:
            try:
                model = None
                model_file = fp / ".model"
                # warm path: check ModelCache before parsing
                if cache_load_fn is not None:
                    model = cache_load_fn(model_file)
                if model is None:
                    key = ("fpr", idx, fp)
                    if preread_bytes is not None and key in preread_bytes:
                        # cold path: parse from preread bytes - zero file I/O
                        model_bytes, mpsr_data = preread_bytes[key]
                        model = _parse_fpr_bytes(model_bytes, mpsr_data, fpr_path=fp)
                        if model is not None and cache_save_fn is not None:
                            cache_save_fn(model_file, model)
                    else:
                        # fallback: when preread is not available then parse from file directly
                        model = parse_fpr(fp)
                if model is not None:
                    solution.models.append(model)
            except Exception as exc:
                warnings.warn(f"Failed to parse {fp}: {exc}")

        for mp in mps_paths:
            try:
                model = None
                # warm run (cache folder exist on disk after first run): check ModelCache before parsing
                if cache_load_fn is not None:
                    model = cache_load_fn(mp)
                if model is None:
                    key = ("mps", idx, mp)
                    if preread_bytes is not None and key in preread_bytes:
                        # cold path: parse from preread bytes - zero file I/O
                        model = _parse_mps_bytes(preread_bytes[key], mps_path=mp)
                        if model is not None and cache_save_fn is not None:
                            cache_save_fn(mp, model)
                    else:
                        # fallback: preread unavailable - parse from file directly
                        model = parse_mps(mp)
                if model is not None:
                    solution.models.append(model)
            except Exception as exc:
                warnings.warn(f"Failed to parse {mp}: {exc}")

        solutions.append(solution)

    return solutions


def _parse_fpr_bytes(model_bytes: bytes, mpsr_data: list, fpr_path: Path = None):
    # parse FPR from pre-read bytes in-process so basically no file I/O.. This is called from disk_thread so basically
    # no shared mutable state between callers.
    # fpr_path is the FPR directory used to set model.path_to_model_file so it matches
    # what SModelBuilderFilePerRootPersistency.build() would actually set..
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
            builder.extract_imports_and_registry(mpsr_xml)
            root = mpsr_xml.find("node")
            if root is not None:
                root_node = builder.extract_node(model, root, None)
                model._root_idxs.append(root_node._idx)
        except Exception:
            pass
    model._finalize()
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
    builder.extract_imports_and_registry(model_xml)
    for node_xml in model_xml.findall("node"):
        root_node = builder.extract_node(model, node_xml, None)
        model._root_idxs.append(root_node._idx)
    model._finalize()
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
    # This is used by SSolutionBuilder for disk-resident MPS models.
    if cache_load_fn is not None:
        cached = cache_load_fn(model_path)
        if cached is not None:
            return cached
    model = _parse_mps_bytes(model_path.read_bytes(), mps_path=model_path)
    if model is not None and cache_save_fn is not None:
        cache_save_fn(model_path, model)
    return model
