# mpscli/model/builder/utils/JarScanner.py
#
# Discovers MPS model content inside JAR files without extracting them to disk. Reads only the ZIP central
# directory (the table of contents at the end of the ZIP file) plus small .msd and .mpl XML members.
# No model bytes are actually readd here.
#
# Produces JarScanResult which SSolutionsRepositoryBuilder uses to drive phases 2-4 so basically the mpb member
# list feeds MpbBatchParser, solution_infos feeds..

import threading
import warnings
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from mpscli.model.SSolution import SSolution
from mpscli.model.builder.utils.JarUtils import jar_is_relevant


class JarSolutionInfo:
    # all MPS content discovered for one solution inside one JAR
    def __init__(self, solution, jar_path_str, mpb_members, mps_members, fpr_prefixes):
        self.solution = solution
        self.jar_path_str = jar_path_str
        # [(jar_path_str, member_name)] given directly to MpbBatchParser.parse_from_jars
        self.mpb_members = mpb_members
        # [member_name] for .mps files within this jar
        self.mps_members = mps_members
        # [prefix] for FPR directories within this JAR, ex: 'module/models/MyModel/'
        self.fpr_prefixes = fpr_prefixes


class JarScanResult:

    def __init__(self):
        # one entry per (.msd, jar) pair so may have duplicates across jars..
        self.solution_infos: List[JarSolutionInfo] = []
        # (namespace, uuid, version, [(jar_path_str, member_name)])
        self.language_infos: List[Tuple[str, str, int, List[Tuple[str, str]]]] = []
        # flat deduplicated list of all (jar_path_str, member_name) for .mpb files
        self.all_mpb_members: List[Tuple[str, str]] = []
        # {jar_path_str: (mtime, size)} collected during scan. ParseCache.load_sync() uses these to validate
        # cache staleness without extra  calls where each JAR is already open so stat() is quite cheap here I think..
        self.jar_stats: Dict[str, Tuple[float, int]] = {}


def scan_jar(jar_path: Path) -> Optional[JarScanResult]:
    if not jar_is_relevant(jar_path):
        return None

    jar_path_str = str(jar_path)
    result = JarScanResult()
    seen_mpbs = set()

    try:
        with zipfile.ZipFile(jar_path_str) as zf:
            try:
                stat = jar_path.stat()
                result.jar_stats[jar_path_str] = (stat.st_mtime, stat.st_size)
            except Exception:
                pass

            names = zf.namelist()
            mpb_names = [n for n in names if n.endswith(".mpb")]
            mps_names = [n for n in names if n.endswith(".mps")]
            fpr_prefixes = [
                n[: -len(".model")]
                for n in names
                if n.endswith("/.model") and "/models/" in n
            ]

            for msd_name in (n for n in names if n.endswith(".msd")):
                try:
                    root = ET.fromstring(zf.read(msd_name))
                    sol_name = root.get("name", "")
                    sol_uuid = root.get("uuid", "")
                    if not sol_name:
                        continue
                    prefix = _models_prefix(msd_name)
                    solution = SSolution(sol_name, sol_uuid)
                    solution.path_to_solution_file = jar_path

                    mpb_members = [
                        (jar_path_str, n) for n in mpb_names if n.startswith(prefix)
                    ]
                    mps_members = [n for n in mps_names if n.startswith(prefix)]
                    sol_fpr = [p for p in fpr_prefixes if p.startswith(prefix)]

                    result.solution_infos.append(
                        JarSolutionInfo(
                            solution, jar_path_str, mpb_members, mps_members, sol_fpr
                        )
                    )
                    for m in mpb_members:
                        if m not in seen_mpbs:
                            seen_mpbs.add(m)
                            result.all_mpb_members.append(m)

                except Exception as exc:
                    warnings.warn(
                        f"Failed to read {msd_name} in {jar_path.name}: {exc}"
                    )

            for mpl_name in (n for n in names if n.endswith(".mpl")):
                try:
                    root = ET.fromstring(zf.read(mpl_name))
                    namespace = root.get("namespace", "")
                    uuid = root.get("uuid", "")
                    version = int(root.get("languageVersion", "0"))
                    if not namespace:
                        continue
                    prefix = _models_prefix(mpl_name)
                    members = [
                        (jar_path_str, n) for n in mpb_names if n.startswith(prefix)
                    ]
                    result.language_infos.append((namespace, uuid, version, members))
                    for m in members:
                        if m not in seen_mpbs:
                            seen_mpbs.add(m)
                            result.all_mpb_members.append(m)
                except Exception as exc:
                    warnings.warn(
                        f"Failed to read {mpl_name} in {jar_path.name}: {exc}"
                    )

    except Exception as exc:
        warnings.warn(f"Failed to scan {jar_path.name}: {exc}")
        return None

    return result


def scan_all_jars(jar_paths: List[Path], workers: int) -> JarScanResult:
    combined = JarScanResult()
    seen_mpbs = set()
    lock = threading.Lock()

    def process_one(jar_path: Path):
        result = scan_jar(jar_path)
        if result is None:
            return
        with lock:
            combined.solution_infos.extend(result.solution_infos)
            combined.language_infos.extend(result.language_infos)
            combined.jar_stats.update(result.jar_stats)
            for m in result.all_mpb_members:
                if m not in seen_mpbs:
                    seen_mpbs.add(m)
                    combined.all_mpb_members.append(m)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(process_one, jp): jp for jp in jar_paths}
        for future in as_completed(futures):
            exc = future.exception()
            if exc:
                warnings.warn(f"Error scanning {futures[future]}: {exc}")

    return combined


def _models_prefix(member_name: str) -> str:
    if "/" in member_name:
        return member_name.rsplit("/", 1)[0] + "/models/"
    return "models/"
