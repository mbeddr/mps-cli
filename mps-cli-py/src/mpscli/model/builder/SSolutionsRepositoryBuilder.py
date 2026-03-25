"""
SSolutionsRepositoryBuilder — builds an SRepository from a directory tree.

Performance optimizations:
  1. Lazy jar scanning: peek inside each zip for .msd before extracting.
     Looks like around 80% of jars (those without .msd) are skipped entirely so no extraction and no scan.
     This is identical to the old code because the original code also only discovered .mpb files through the .msd - models/
     chain and a jar without .msd was always skipped.
  2. Parallel jar processing: extract/scan/parse/cleanup in a thread pool (i/o-bound work) so ThreadPoolExecutor is ideal.
  3. Persistent disk cache: parsed SModel objects moved to mps_cli_cache and unchanged files load in probably milliseconds
     and cache is invalidated automatically when a file changes.
"""

from timeit import default_timer as timer
import os
import sys
import zipfile
import shutil
import pickle
import hashlib
import tempfile
import threading
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from mpscli.model.SRepository import SRepository
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.SSolutionBuilder import SSolutionBuilder

_CACHE_DIR: Path | None = None
_CACHE_DIR_LOCK = threading.Lock()


def _get_cache_dir() -> Path:
    global _CACHE_DIR
    with _CACHE_DIR_LOCK:
        if _CACHE_DIR is None:
            d = Path.home() / ".mps_cli_cache"
            d.mkdir(exist_ok=True)
            _CACHE_DIR = d
    return _CACHE_DIR


def _cache_key(path: Path) -> str:
    stat = path.stat()
    raw = f"{path}|{stat.st_mtime}|{stat.st_size}"
    return hashlib.md5(raw.encode()).hexdigest()


def _load_cached(path: Path):
    # return cached SModel if file is unchanged, else return None
    try:
        key = _cache_key(path)
        cache_file = _get_cache_dir() / key
        if cache_file.exists():
            with cache_file.open("rb") as f:
                return pickle.load(f)
    except Exception:
        pass
    return None


def _save_cached(path: Path, model) -> None:
    # persist a parsed SModel to the cache
    try:
        key = _cache_key(path)
        cache_file = _get_cache_dir() / key
        with cache_file.open("wb") as f:
            pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:
        pass


def _jar_has_msd(jar_path: Path) -> bool:
    """
    Peek inside a zip/jar to check for .msd files without extracting.
    Reads only the ZIP central directory.
    """

    try:
        with zipfile.ZipFile(jar_path) as zf:
            return any(name.endswith(".msd") for name in zf.namelist())
    except Exception:
        return False


class SSolutionsRepositoryBuilder:

    # number of threads for parallel jar processing.  None = auto (up to 16).
    JAR_THREADS: int | None = None

    # set false to disable the persistent cache and always re-parse
    USE_CACHE: bool = True

    def __init__(self):
        self.repo = SRepository()
        self._repo_lock = threading.Lock()

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

            self.collect_solutions_from_sources(path)
            self.collect_solutions_from_jars(path)

        self.repo.languages = list(SLanguageBuilder.languages.values())

        stop = timer()
        print(f"duration for parsing modules: {stop - start:.2f} seconds")
        return self.repo

    def collect_solutions_from_sources(self, path):
        msd_paths = list(Path(path).rglob("*.msd"))
        if not msd_paths:
            return

        builder = SSolutionBuilder()
        if self.USE_CACHE:
            builder.USE_CACHE = True
            builder.CACHE_LOAD_FN = _load_cached
            builder.CACHE_SAVE_FN = _save_cached

        solutions = builder.build_all(msd_paths)

        with self._repo_lock:
            for solution in solutions:
                if solution is not None and not self.repo.find_solution_by_name(
                    solution.name
                ):
                    self.repo.solutions.append(solution)

    def collect_solutions_from_jars(self, path):
        """
        For every JAR under 'path':
          1. Peek inside the zip central directory (no extraction) and skip if no .msd file
          2. Extract to a private temp directory.
          3. collect_solutions_from_sources() on the temp dir
          4. Delete the temp dir unconditionally.
        now all jars are processed concurrently via a ThreadPoolExecutor.
        """
        jar_paths = list(Path(path).rglob("*.jar"))
        if not jar_paths:
            return

        workers = self.JAR_THREADS or min(os.cpu_count() or 4, 16)

        def _process_jar(jar_path: Path):
            # cheap peek: skip jarss with no .msd
            if not _jar_has_msd(jar_path):
                return

            # extract to an isolated temp directory
            extract_dir = jar_path.parent / jar_path.name.replace(".", "_")
            extract_dir.mkdir(parents=True, exist_ok=True)
            try:
                with zipfile.ZipFile(jar_path) as jar:
                    jar.extractall(extract_dir)
                # print just the jar name
                print(f"extracting: {jar_path.name}")

                # scan and parse
                self.collect_solutions_from_sources(extract_dir)

            finally:
                # always clean up
                try:
                    shutil.rmtree(extract_dir)
                except OSError as e:
                    print(f"Error removing {extract_dir}: {e}")

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_process_jar, jp): jp for jp in jar_paths}
            for future in as_completed(futures):
                exc = future.exception()
                if exc:
                    warnings.warn(f"Error processing {futures[future]}: {exc}")
