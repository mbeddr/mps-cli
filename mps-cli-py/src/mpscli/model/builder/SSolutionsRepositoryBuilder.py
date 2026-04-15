"""
SSolutionsRepositoryBuilder - builds an SRepository from a directory tree.
"""

from timeit import default_timer as timer
import os
import sys
import zipfile
import shutil
import warnings
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from mpscli.model.SRepository import SRepository
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.SSolutionBuilder import SSolutionBuilder
from mpscli.model.builder.utils.MpbBatchParser import MpbBatchParser
from mpscli.model.builder.utils.ModelCache import ModelCache


def _jar_is_relevant(jar_path: Path) -> bool:
    # peek inside a zip/jar to check for .msd or .mpl files without extracting where only the ZIP
    # central directory is read
    # A jar is worth extracting if it contains:
    # .msd - solution descriptor
    # .mpl - language descriptor
    try:
        with zipfile.ZipFile(jar_path) as zf:
            names = zf.namelist()
            return any(name.endswith(".msd") or name.endswith(".mpl") for name in names)
    except Exception:
        return False


class SSolutionsRepositoryBuilder:

    # number of threads for parallel jar processing
    JAR_THREADS: int | None = None

    # Set False to disable the persistent cache and always reparse from disk
    USE_CACHE: bool = True

    def __init__(self):
        self.repo = SRepository()
        self._repo_lock = threading.Lock()
        self._cache = ModelCache()

    def build(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        elif not isinstance(paths, list):
            print("ERROR: paths should be either a string or a list of strings!")
            sys.exit(1)

        start = timer()
        for path in paths:
            if not os.path.exists(path):
                warnings.warn(f"Path not found: {path}")
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
        mpb_parser = MpbBatchParser(
            use_cache=self.USE_CACHE,
            cache_load_fn=self._cache.load if self.USE_CACHE else None,
            cache_save_fn=self._cache.save if self.USE_CACHE else None,
        )

        builder = SSolutionBuilder()
        solutions = builder.build_all(msd_paths, mpb_parser=mpb_parser)

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
          Now all jars are processed concurrently via a ThreadPoolExecutor
        """
        jar_paths = list(Path(path).rglob("*.jar"))
        if not jar_paths:
            return

        workers = self.JAR_THREADS or min(os.cpu_count() or 4, 16)

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(self._process_jar, jp): jp for jp in jar_paths}
            for future in as_completed(futures):
                exc = future.exception()
                if exc:
                    warnings.warn(f"Error processing {futures[future]}: {exc}")

    def _process_jar(self, jar_path: Path) -> None:
        # cheap peek - skip jars with neither a .msd nor .mpl file
        if not _jar_is_relevant(jar_path):
            return
        # extract to an isolated temp directory
        extract_dir = jar_path.parent / jar_path.name.replace(".", "_")
        extract_dir.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(jar_path) as jar:
                jar.extractall(extract_dir)
            # print just the jar name
            print(f"extracting: {jar_path.name}")
            # scan and also parse solutions (.msd and models)
            self.collect_solutions_from_sources(extract_dir)
            # read any .mpl files to populate SLanguage objects with version and aspect models
            for mpl_file in extract_dir.rglob("*.mpl"):
                SLanguageBuilder.load_from_mpl(mpl_file)

        finally:
            # always clean up
            try:
                shutil.rmtree(extract_dir)
            except OSError as e:
                print(f"Error removing {extract_dir}: {e}")
