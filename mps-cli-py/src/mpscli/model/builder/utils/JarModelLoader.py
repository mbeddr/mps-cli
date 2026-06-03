# mpscli/model/builder/utils/JarModelLoader.py
#
# Builds SSolution objects from JAR scan results. For FPR/MPS: ThreadPool preread bytes + ProcessPool compute
# Also, uses ParseCache (one file loaded once) instead of per JAR files

import warnings
import zipfile
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from contextlib import nullcontext
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import threading

from mpscli.model.SSolution import SSolution
from mpscli.model.builder.utils.JarScanner import JarScanResult, JarSolutionInfo

# minimum number of FPR/MPS tasks before spawning a ProcessPool for phase 4
# below this threshold tasks run serially to avoid Windows process spawn overhead..
_FPR_POOL_THRESHOLD = 8


def _parse_fpr_bytes_worker(model_bytes: bytes, mpsr_data: list):
    # top-level picklable which is pure compute so basically no ZIP I/O
    # returns (model, new_lang_pairs) with (name, uuid) only and not the concept data. see
    # _parse_jar_members_batch_worker for explanation on why concept data is not returned from pool workers
    try:
        from lxml import etree as ET
    except ImportError:
        import xml.etree.ElementTree as ET
    from mpscli.model.builder.SModelBuilderFilePerRootPersistency import (
        SModelBuilderFilePerRootPersistency,
    )
    from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder

    existing_names = set(SLanguageBuilder.languages.keys())

    builder = SModelBuilderFilePerRootPersistency()
    model_xml = ET.fromstring(model_bytes)
    model = builder.extract_model_core_info(model_xml)
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

    new_lang_pairs = [
        (name, lang.uuid)
        for name, lang in SLanguageBuilder.languages.items()
        if name not in existing_names
    ]
    return model, new_lang_pairs


def _parse_mps_bytes_worker(data: bytes):
    # top-level picklable so again pure compute and no ZIP I/O.
    # returns (model, new_lang_pairs) with (name, uuid) only, see _parse_fpr_bytes_worker comment
    try:
        from lxml import etree as ET
    except ImportError:
        import xml.etree.ElementTree as ET
    from mpscli.model.builder.SModelBuilderDefaultPersistency import (
        SModelBuilderDefaultPersistency,
    )
    from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder

    existing_names = set(SLanguageBuilder.languages.keys())

    builder = SModelBuilderDefaultPersistency()
    model_xml = ET.fromstring(data)
    model = builder.extract_model_core_info(model_xml)
    builder.extract_imports_and_registry(model_xml)
    for node_xml in model_xml.findall("node"):
        root_node = builder.extract_node(model, node_xml, None)
        model._root_idxs.append(root_node._idx)
    model._finalize()

    new_lang_pairs = [
        (name, lang.uuid)
        for name, lang in SLanguageBuilder.languages.items()
        if name not in existing_names
    ]
    return model, new_lang_pairs


def _preread_fpr_bytes(
    infos: List[JarSolutionInfo], workers: int
) -> Dict[Tuple[str, str], Tuple[bytes, list]]:
    # this is I/O bound: ThreadPoolExecutor opens each unique JAR exactly once
    by_jar: Dict[str, List[str]] = defaultdict(list)
    for info in infos:
        for prefix in info.fpr_prefixes:
            by_jar[info.jar_path_str].append(prefix)

    if not by_jar:
        return {}

    results: Dict[Tuple[str, str], Tuple[bytes, list]] = {}
    lock = threading.Lock()

    def read_jar(jar_path_str: str, prefixes: List[str]) -> None:
        jar_data = {}
        try:
            with zipfile.ZipFile(jar_path_str) as zf:
                names = zf.namelist()
                for prefix in prefixes:
                    try:
                        model_bytes = zf.read(prefix + ".model")
                        mpsr_data = [
                            (n, zf.read(n))
                            for n in sorted(
                                m
                                for m in names
                                if m.startswith(prefix) and m.endswith(".mpsr")
                            )
                        ]
                        jar_data[(jar_path_str, prefix)] = (model_bytes, mpsr_data)
                    except Exception:
                        pass
        except Exception as exc:
            warnings.warn(f"Failed to pre-read fpr from {jar_path_str}: {exc}")
        with lock:
            results.update(jar_data)

    # use many threads to overlap delay across all jars..
    io_threads = min(len(by_jar) * 2, 200)
    with ThreadPoolExecutor(max_workers=io_threads) as pool:
        futures = {
            pool.submit(read_jar, jar, prefixes): jar
            for jar, prefixes in by_jar.items()
        }
        for future in as_completed(futures):
            exc = future.exception()
            if exc:
                warnings.warn(f"Error pre-reading {futures[future]}: {exc}")

    return results


def preread_all_fpr_bytes(
    scan: JarScanResult, workers: int
) -> Dict[Tuple[str, str], Tuple[bytes, list]]:
    # preread FPR bytes for all solution_infos in the scan result.
    return _preread_fpr_bytes(scan.solution_infos, workers)


def load_jar_solutions(
    scan: JarScanResult,
    jar_results: Dict[Tuple[str, str], object],
    disk_solution_names: Set[str],
    workers: int,
    parse_cache=None,
    use_cache: bool = True,
    pool: Optional[ProcessPoolExecutor] = None,
    prereaded_fpr: Optional[Dict] = None,
    jar_stats: Optional[Dict[str, Tuple[float, int]]] = None,
) -> List[SSolution]:
    from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
    from mpscli.model.builder.utils.MpbBatchParser import _register_lang_pairs

    seen = set(disk_solution_names)
    winners: List[JarSolutionInfo] = []
    for info in scan.solution_infos:
        if info.solution.name not in seen:
            seen.add(info.solution.name)
            winners.append(info)

    if not winners:
        return []

    solution_by_name: Dict[str, SSolution] = {}
    for info in winners:
        solution_by_name[info.solution.name] = info.solution
        for key in info.mpb_members:
            model = jar_results.get(key)
            if model is not None:
                info.solution.models.append(model)

    # check ParseCache
    by_jar_fpr: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    by_jar_mps: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    for info in winners:
        jar = info.jar_path_str
        cached = parse_cache.get_xml(jar) if (use_cache and parse_cache) else None
        if cached is not None:
            for prefix in info.fpr_prefixes:
                model = cached.get(("fpr", prefix))
                if model is not None:
                    info.solution.models.append(model)
            for member in info.mps_members:
                model = cached.get(("mps", member))
                if model is not None:
                    info.solution.models.append(model)
        else:
            for prefix in info.fpr_prefixes:
                by_jar_fpr[jar].append((info.solution.name, prefix))
            for member in info.mps_members:
                by_jar_mps[jar].append((info.solution.name, member))

    has_fpr = any(by_jar_fpr.values())
    has_mps = any(by_jar_mps.values())

    if not has_fpr and not has_mps:
        return list(solution_by_name.values())

    # use prereaded bytes if provided otherwise read now
    if prereaded_fpr is not None:
        fpr_bytes = prereaded_fpr
    elif has_fpr:
        fpr_bytes = _preread_fpr_bytes(winners, workers)
    else:
        fpr_bytes = {}

    mps_bytes: Dict[Tuple[str, str], bytes] = {}
    if has_mps:
        # use many concurrent threads to overlap delay across all MPS JARs.
        mps_lock = threading.Lock()

        def read_mps_jar(jar_entries):
            jar, entries = jar_entries
            jar_data = {}
            try:
                with zipfile.ZipFile(jar) as zf:
                    for _sol_name, member in entries:
                        try:
                            jar_data[(jar, member)] = zf.read(member)
                        except Exception:
                            pass
            except Exception as exc:
                warnings.warn(f"Failed to pre-read mps from {jar}: {exc}")
            with mps_lock:
                mps_bytes.update(jar_data)

        io_threads = min(len(by_jar_mps) * 2, 200)
        with ThreadPoolExecutor(max_workers=io_threads) as mps_pool:
            list(mps_pool.map(read_mps_jar, by_jar_mps.items()))

    all_tasks = []
    for jar, entries in by_jar_fpr.items():
        for sol_name, prefix in entries:
            byte_data = fpr_bytes.get((jar, prefix))
            if byte_data is not None:
                model_bytes, mpsr_data = byte_data
                all_tasks.append(("fpr", sol_name, jar, prefix, model_bytes, mpsr_data))
    for jar, entries in by_jar_mps.items():
        for sol_name, member in entries:
            data = mps_bytes.get((jar, member))
            if data is not None:
                all_tasks.append(("mps", sol_name, jar, member, data, None))

    if not all_tasks:
        return list(solution_by_name.values())

    jar_cache_pending: Dict[str, Dict] = defaultdict(dict)

    def _handle_result(model, lang_pairs, kind, sol_name, jar, key):
        sol = solution_by_name.get(sol_name)
        if sol is not None:
            sol.models.append(model)
        jar_cache_pending[jar][(kind, key)] = model
        # register language shells from subprocess workers
        if lang_pairs:
            _register_lang_pairs(lang_pairs)

    # only spawn workers when there are enough tasks to justify the overhead. The passed pool is used when
    # above threshold and serial path is usd when below, task count drives the decision not pool presence so this
    # ensures small test projects always parse in the main process so SLanguageBuilder gets populated...
    if len(all_tasks) >= _FPR_POOL_THRESHOLD:
        pool_ctx = (
            nullcontext(pool)
            if pool is not None
            else ProcessPoolExecutor(max_workers=workers)
        )
        with pool_ctx as _pool:
            future_to_info = {}
            for task in all_tasks:
                kind, sol_name, jar, key = task[0], task[1], task[2], task[3]
                f = (
                    _pool.submit(_parse_fpr_bytes_worker, task[4], task[5])
                    if kind == "fpr"
                    else _pool.submit(_parse_mps_bytes_worker, task[4])
                )
                future_to_info[f] = (kind, sol_name, jar, key)

            for future in as_completed(future_to_info):
                kind, sol_name, jar, key = future_to_info[future]
                try:
                    model, lang_pairs = future.result()
                    _handle_result(model, lang_pairs, kind, sol_name, jar, key)
                except Exception as exc:
                    warnings.warn(f"Failed to parse {jar}!{key}: {exc}")
    else:
        # serial path for small batches so no pool spawn overhead and languages are populated in-process
        for task in all_tasks:
            kind, sol_name, jar, key = task[0], task[1], task[2], task[3]
            try:
                if kind == "fpr":
                    model, lang_pairs = _parse_fpr_bytes_worker(task[4], task[5])
                else:
                    model, lang_pairs = _parse_mps_bytes_worker(task[4])
                _handle_result(model, lang_pairs, kind, sol_name, jar, key)
            except Exception as exc:
                warnings.warn(f"Failed to parse {jar}!{key}: {exc}")

    # update ParseCache synchronously so basically just dict assignments and no I/O
    if use_cache and parse_cache and jar_cache_pending:
        parse_cache.put_xml_many(dict(jar_cache_pending), jar_stats)

    return list(solution_by_name.values())
