"""
SSolutionsRepositoryBuilder - builds an SRepository from a directory tree.
"""

import logging
import os
import sys
import threading
import warnings
from timeit import default_timer as timer
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict

from mpscli.model.SRepository import SRepository
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.utils.MpbBatchParser import MpbBatchParser
from mpscli.model.builder.utils.ModelCache import ModelCache
from mpscli.model.builder.utils.JarScanner import scan_all_jars
from mpscli.model.builder.utils.JarModelLoader import load_jar_solutions
from mpscli.model.builder.utils.ParseCache import ParseCache

_log = logging.getLogger(__name__)

# minimum number of unique jars with mpb members before spawning a ProcessPool.. this is measured in jars
# amd not members so spawning overhead is per-pool not per-task n  each jar worker
# opens one ZIP file, so jar count drives the parallelism benefit...
_JAR_POOL_THRESHOLD = 8


class SSolutionsRepositoryBuilder:

    # number of threads for parallel jar processing
    JAR_THREADS: int | None = None

    # Set False to disable the persistent cache and always reparse from disk
    USE_CACHE: bool = True

    def __init__(self):
        self.repo = SRepository()
        self._repo_lock = threading.Lock()
        self._disk_cache = ModelCache() if self.USE_CACHE else None
        self._parse_cache = (
            ParseCache(workers=min(os.cpu_count() or 4, 16)) if self.USE_CACHE else None
        )
        self._mpb_parser = MpbBatchParser(
            use_cache=self.USE_CACHE,
            cache_load_fn=self._disk_cache.load if self._disk_cache else None,
            cache_save_fn=self._disk_cache.save if self._disk_cache else None,
        )
        # workers=1 so no ProcessPool is spawned I think during disk mpb parsing..
        # also I guess this prevents GIL contention with load_sync ThreadPool...
        self._disk_mpb_parser = MpbBatchParser(
            workers=1,
            use_cache=self.USE_CACHE,
            cache_load_fn=self._disk_cache.load if self._disk_cache else None,
            cache_save_fn=self._disk_cache.save if self._disk_cache else None,
        )

    def build(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        elif not isinstance(paths, list):
            _log.error("paths should be either a string or a list of strings")
            sys.exit(1)

        start = timer()
        valid_paths = [p for p in paths if self._is_valid_path(p)]
        if valid_paths:
            self.collect_solutions_from_jars(valid_paths)
        self.repo.languages = list(SLanguageBuilder.languages.values())
        stop = timer()
        _log.info("duration for parsing modules: %.2f seconds", stop - start)
        if self._parse_cache:
            self._parse_cache.flush()
        return self.repo

    def collect_solutions_from_sources(
        self, paths, msd_paths=None, preread_bytes=None, workers=1, msd_stats=None
    ):
        # disk FPR/MPS parsing and this runs after phase4 with workers=16 (ProcessPool) so phase3 getss
        # all 16 cores. SLanguageBuilder locking will also ensure thread safety if ever called
        # concurrently in the future...
        if msd_paths is None:
            msd_paths = [p for path in paths for p in Path(path).rglob("*.msd")]
        if not msd_paths:
            return
        t0 = timer()
        from mpscli.model.builder.utils.DiskModelLoader import load_disk_solutions

        solutions = load_disk_solutions(
            msd_paths,
            mpb_parser=self._disk_mpb_parser,
            preread_bytes=preread_bytes,
            cache_load_fn=self._disk_cache.load if self._disk_cache else None,
            cache_save_fn=self._disk_cache.save if self._disk_cache else None,
            workers=workers,
            parse_cache=self._parse_cache,
            msd_stats=msd_stats,
        )
        with self._repo_lock:
            for solution in solutions:
                if solution is None:
                    continue
                existing = self.repo.find_solution_by_name(solution.name)
                if existing is None:
                    self.repo.solutions.append(solution)
                else:
                    # jar solution already exists so merge disk models into it
                    existing_uuids = {m.uuid for m in existing.models}
                    for model in solution.models:
                        if model.uuid not in existing_uuids:
                            existing.models.append(model)
                            existing_uuids.add(model.uuid)
        _log.info(
            "[diag] phase3 disk: %.1fs -- %d msd files", timer() - t0, len(msd_paths)
        )

    def collect_solutions_from_jars(self, paths):
        workers = self.JAR_THREADS or min(os.cpu_count() or 4, 16)

        # phase1: scan ZIP central directories.
        t0 = timer()
        jar_paths = [jp for path in paths for jp in Path(path).rglob("*.jar")]
        scan = scan_all_jars(jar_paths, workers)
        t1 = timer()
        _log.info(
            "[diag] phase1 scan: %.1fs -- %d jar solutions, %d languages, %d mpb members",
            t1 - t0,
            len(scan.solution_infos),
            len(scan.language_infos),
            len(scan.all_mpb_members),
        )

        if self._parse_cache:
            t_load = timer()
            self._parse_cache.load_sync(scan.jar_stats)
            _log.info("[diag] cache load: %.1fs", timer() - t_load)

        # scan disk msd files and start I/O pre-read before phase2.. preread is a ThreadPool
        # reading model/.mpsr bytes which is pure I/O. This also runs concurrently with phase2 ProcessPool...
        msd_paths = sorted([p for path in paths for p in Path(path).rglob("*.msd")])
        preread_bytes: dict = {}
        preread_thread = None
        if msd_paths:
            from mpscli.model.builder.utils.DiskModelLoader import preread_disk_bytes

            def _do_preread():
                preread_bytes.update(preread_disk_bytes(msd_paths))

            preread_thread = threading.Thread(
                target=_do_preread, daemon=True, name="disk-preread"
            )
            preread_thread.start()

        # phase2 - parse JAR .mpb members
        # So on cold runs workers read bytes from jars, parse, cache bytes for next run and on warm runs
        # workers reparse cached bytes with no jar I/O and the pool thresholdd is measured in unique JARs since
        # each worker handles one jar and pool spawn overhead is shared across jar count and not the member count.
        t2_start = timer()
        unique_jars = len({jar for jar, _ in scan.all_mpb_members})
        use_pool = unique_jars >= _JAR_POOL_THRESHOLD
        pool = ProcessPoolExecutor(max_workers=workers) if use_pool else None

        try:
            jar_results = self._mpb_parser.parse_from_jars(
                scan.all_mpb_members, pool=pool
            )
            t2 = timer()
            _log.info(
                "[diag] phase2 jar mpb: %.1fs -- %d models",
                t2 - t2_start,
                len(jar_results),
            )

            # join preread which should already be done..
            if preread_thread is not None:
                preread_thread.join()

            # build msd_stats for disk cache validationn (mtime+size per .msd file)
            msd_stats = {}
            for p in msd_paths:
                try:
                    st = p.stat()
                    msd_stats[str(p)] = (st.st_mtime, st.st_size)
                except Exception:
                    pass
            if self._parse_cache is not None:
                self._parse_cache.load_disk_sync(msd_stats)

            # phase4: jar FPR/MPS solutions and this runs before phase3 so each phase get full CPU without competing.. phase4 uses the shared ProcessPool.
            disk_solution_names = {s.name for s in self.repo.solutions}
            jar_solutions = load_jar_solutions(
                scan,
                jar_results,
                disk_solution_names,
                workers,
                parse_cache=self._parse_cache,
                use_cache=self.USE_CACHE,
                pool=pool,
                prereaded_fpr=None,
                jar_stats=scan.jar_stats,
            )
            t3 = timer()

            # phase3: disk FPR/MPS and this runs after phase4 with full ProcessPool (workers=16).
            self.collect_solutions_from_sources(
                paths,
                msd_paths=msd_paths,
                preread_bytes=preread_bytes or None,
                workers=workers,
                msd_stats=msd_stats,
            )

        finally:
            if pool is not None:
                # wait=False beacuse disk already joined above so workers idle since phase4
                pool.shutdown(wait=False)

        with self._repo_lock:
            for solution in jar_solutions:
                existing = self.repo.find_solution_by_name(solution.name)
                if existing is None:
                    self.repo.solutions.append(solution)
                else:
                    # disk solution already in repo so merge jar models into it
                    existing_uuids = {m.uuid for m in existing.models}
                    for model in solution.models:
                        if model.uuid not in existing_uuids:
                            existing.models.append(model)
                            existing_uuids.add(model.uuid)

        total = sum(len(s.models) for s in self.repo.solutions)
        _log.info(
            "[diag] phase4 fpr/mps: %.1fs -- %d solutions, %d models",
            t3 - t2,
            len(self.repo.solutions),
            total,
        )

        t4 = timer()
        for namespace, uuid, version, mpb_members in scan.language_infos:
            lang = SLanguageBuilder.get_language(namespace, uuid)
            lang.language_version = version
            lang.models = [
                jar_results[key]
                for key in mpb_members
                if jar_results.get(key) is not None
            ]
        _log.info("[diag] phase5 lang: %.1fs", timer() - t4)

    def _is_valid_path(self, path: str) -> bool:
        if not os.path.exists(path):
            warnings.warn(f"Path not found: {path}")
            return False
        if not os.path.isdir(path):
            _log.error("path %s is not a directory", path)
            return False
        return True
