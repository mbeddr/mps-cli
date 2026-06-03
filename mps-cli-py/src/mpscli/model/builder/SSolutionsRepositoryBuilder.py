"""
SSolutionsRepositoryBuilder - builds an SRepository from a directory tree.
"""

import logging
import os
import sys
import threading
import warnings
from timeit import default_timer as timer
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict

from mpscli.model.SRepository import SRepository
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.utils.MpbBatchParser import (
    MpbBatchParser,
    _parse_jar_members_batch_worker,
    _register_lang_pairs,
)
from mpscli.model.builder.utils.ModelCache import ModelCache
from mpscli.model.builder.utils.JarScanner import scan_all_jars
from mpscli.model.builder.utils.JarModelLoader import load_jar_solutions
from mpscli.model.builder.utils.ParseCache import ParseCache

_log = logging.getLogger(__name__)

# minimum number of JAR batches before spawning a ProcessPool...
_JAR_POOL_THRESHOLD = 8


class SSolutionsRepositoryBuilder:

    JAR_THREADS: int | None = None
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
            parse_cache=self._parse_cache,
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

    def collect_solutions_from_sources(self, paths, msd_paths=None, preread_bytes=None):
        # disk .msd files are always serial for FPR/MPS so SLanguageBuilder.get_concept is called in this thread
        # and concepts are populated correctly for test projects
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
        )
        with self._repo_lock:
            for solution in solutions:
                if solution is not None and not self.repo.find_solution_by_name(
                    solution.name
                ):
                    self.repo.solutions.append(solution)
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

        jar_cached, uncached_by_jar = self._mpb_parser.get_cached_and_uncached_by_jar(
            scan.all_mpb_members
        )
        jar_results = dict(jar_cached)
        hits = len(jar_cached)
        misses = sum(len(v) for v in uncached_by_jar.values())
        _log.info("[diag] cache: %d hits, %d misses", hits, misses)

        # scan disk msd files and start I/O pre-read before phase2. preread is a ThreadPool reading model/.mpsr bytes which is
        # pure I/O. This also runs concurrently with phase2's ProcessPool (so basically separate processes, no conflict)..
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

        # phase2: parse uncached JAR .mpb members..
        # single pool spanning phase2 and phase4 - spawn happens once, before disk_thread, so no second SPAWN event
        # most probably occurs after disk_thread starts.
        jar_new: Dict[str, dict] = {}
        t2_start = timer()
        use_pool = len(uncached_by_jar) >= _JAR_POOL_THRESHOLD
        pool = ProcessPoolExecutor(max_workers=workers) if use_pool else None

        try:
            if pool is not None:
                futures = {
                    pool.submit(_parse_jar_members_batch_worker, jar, members): jar
                    for jar, members in uncached_by_jar.items()
                }
                for future in as_completed(futures):
                    jar = futures[future]
                    try:
                        batch, lang_pairs = future.result()
                        jar_new[jar] = batch
                        for member, model in batch.items():
                            jar_results[(jar, member)] = model
                        if lang_pairs:
                            _register_lang_pairs(lang_pairs)
                    except Exception as exc:
                        warnings.warn(f"Failed to parse JAR {jar}: {exc}")
            else:
                for jar, members in uncached_by_jar.items():
                    try:
                        batch, lang_pairs = _parse_jar_members_batch_worker(
                            jar, members
                        )
                        jar_new[jar] = batch
                        for member, model in batch.items():
                            jar_results[(jar, member)] = model
                        if lang_pairs:
                            _register_lang_pairs(lang_pairs)
                    except Exception as exc:
                        warnings.warn(f"Failed to parse JAR {jar}: {exc}")

            self._mpb_parser.flush_jar_cache(jar_new, scan.jar_stats)
            t2 = timer()
            _log.info(
                "[diag] phase2 jar mpb: %.1fs -- %d models",
                t2 - t2_start,
                len(jar_results),
            )

            # join preread which should already be done
            if preread_thread is not None:
                preread_thread.join()

            # disk_thread starts here and pool already spawned so no second SPAWN event.. This starts after phase2
            # so disk does not compete with phase2 workerss
            disk_thread = threading.Thread(
                target=self.collect_solutions_from_sources,
                args=(paths,),
                kwargs={
                    "msd_paths": msd_paths,
                    "preread_bytes": preread_bytes or None,
                },
                daemon=False,
                name="disk-build",
            )
            disk_thread.start()

            # phase4: JAR FPR/MPS solutions
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

            disk_thread.join()

        finally:
            if pool is not None:
                # wait=False: disk already joined above so the workers idle since phase4..
                pool.shutdown(wait=False)

        with self._repo_lock:
            for solution in jar_solutions:
                if not self.repo.find_solution_by_name(solution.name):
                    self.repo.solutions.append(solution)

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
