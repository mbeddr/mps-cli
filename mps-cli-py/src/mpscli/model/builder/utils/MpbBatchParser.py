# mpscli/model/builder/MpbBatchParser.py
#
# Parallel and cached batch parser for .mpb model files.
#
# Usage:
#   parser = MpbBatchParser(workers, use_cache, cache_load_fn, cache_save_fn)
#   results = parser.parse(list_of_path_strings)
#   results is a dict - {path_str - SModel | None}

import os
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Dict, List, Optional


def _parse_mpb_worker(path_str: str):
    # top-level function (not a method) so it is picklable for ProcessPoolExecutor. Each worker process constructs
    # its own SModelBuilderBinaryPersistency instance and the builder is stateful (index maps, string table)
    # so it must not be shared..
    from mpscli.model.builder.SModelBuilderBinaryPersistency import (
        SModelBuilderBinaryPersistency,
    )

    builder = SModelBuilderBinaryPersistency()
    return builder.build(path_str)


class MpbBatchParser:
    # threshold below which a process pool is not used - spawning workers has fixed overhead of around 100 or 200ms
    # that is good for small batches
    PARALLEL_THRESHOLD: int = 4

    def __init__(
        self,
        workers: Optional[int] = None,
        use_cache: bool = False,
        cache_load_fn: Optional[Callable[[Path], object]] = None,
        cache_save_fn: Optional[Callable[[Path, object], None]] = None,
    ):
        # workers: number of parallel processes for large batches.
        # if use_cache is set to True then cache_load_fn and cache_save_fn are called before/after each parse to
        # avoid reparsing unchanged files..
        self._workers = workers
        self._use_cache = use_cache
        self._cache_load_fn = cache_load_fn
        self._cache_save_fn = cache_save_fn

    def parse(self, path_strings: List[str]) -> Dict[str, object]:
        # Parse all .mpb files in path_strings, returning a dict of {path_str - SModel | None}
        #
        # workflow explained below:
        #   1. Check cache for each path
        #   2. For the remaining (uncached) paths:
        #      :if batch is small (<= PARALLEL_THRESHOLD) or workers == 1 then parse serially
        #      :otherwise dispatch to a ProcessPoolExecutor
        #   3. Save newly parsed models to cache.
        #
        # We use both ProcessPoolExecutor and ThreadPoolExecutor since .mpb parsing is
        # cpu-bound (binary decode + struct unpacking), so processes avoid the GIL and give true parallelism
        # where each worker imports the builder fresh so no shared state.

        if not path_strings:
            return {}

        results: Dict[str, object] = {}
        workers = self._workers or min(os.cpu_count() or 4, 16)

        # phase 1: cache check..
        uncached: List[str] = []
        for ps in path_strings:
            cached = (
                self._cache_load_fn(Path(ps))
                if self._use_cache and self._cache_load_fn
                else None
            )
            if cached is not None:
                results[ps] = cached
            else:
                uncached.append(ps)

        if not uncached:
            return results

        # phase2 - parse uncached paths
        use_pool = workers > 1 and len(uncached) > self.PARALLEL_THRESHOLD

        if not use_pool:
            # serial path - simple and no spawn overhead so it's sufficient for small batches
            for ps in uncached:
                try:
                    model = _parse_mpb_worker(ps)
                    results[ps] = model
                    self._maybe_save_cache(ps, model)
                except Exception as exc:
                    warnings.warn(f"Failed to parse {ps}: {exc}")
                    results[ps] = None
        else:
            # parallel path - one process per worker and each parses independently
            import multiprocessing

            multiprocessing.freeze_support()

            with ProcessPoolExecutor(max_workers=workers) as pool:
                future_to_path = {
                    pool.submit(_parse_mpb_worker, ps): ps for ps in uncached
                }
                for future in as_completed(future_to_path):
                    ps = future_to_path[future]
                    try:
                        model = future.result()
                        results[ps] = model
                        self._maybe_save_cache(ps, model)
                    except Exception as exc:
                        warnings.warn(f"Failed to parse {ps}: {exc}")
                        results[ps] = None

        return results

    def _maybe_save_cache(self, path_str: str, model) -> None:
        # ssave to cache only if caching is enabled, a save function is provided and the model was actually
        # parsed successfully
        if self._use_cache and self._cache_save_fn and model is not None:
            self._cache_save_fn(Path(path_str), model)
