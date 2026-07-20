# mpscli/model/builder/utils/MpbBatchParser.py
#
# Parallel batch parser for .mpb binary model files.
# Handles caching via ModelCache callbacks and parallel execution via ProcessPoolExecutor.
# parse_from_jars handles .mpb files inside JARs - reads bytes directly without extraction.
# FPR and MPS parsing lives in DiskModelLoader.

import os
import warnings
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import nullcontext
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple


def _parse_mpb_worker(path_str: str):
    # top-level so it is picklable for ProcessPoolExecutor.. and each worker constructs its own builder
    # meaning the builder is stateful (index maps, string tables) and must not be shared
    # across processes..
    from mpscli.model.builder.SModelBuilderBinaryPersistency import (
        SModelBuilderBinaryPersistency,
    )

    return SModelBuilderBinaryPersistency().build(path_str)


def _parse_jar_members_batch_worker(jar_path_str: str, member_names: List[str]):
    # top-level which is picklable for ProcessPoolExecutor and each worker opens its own JAR
    # directly on the local disk.
    # reading bytes inside workers (fully parallel) and returning only SModel objects via IPC is I think faster
    # than pre-reading bytes in the main process and sending them to workers since that adds a second IPC
    # round-trip with no I/O saving on local disk..
    import zipfile
    from mpscli.model.builder.SModelBuilderBinaryPersistency import (
        SModelBuilderBinaryPersistency,
    )
    from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder

    existing_names = set(SLanguageBuilder.languages.keys())
    results = {}
    with zipfile.ZipFile(jar_path_str) as zf:
        for member_name in member_names:
            try:
                data = zf.read(member_name)
                results[
                    member_name
                ] = SModelBuilderBinaryPersistency().build_from_bytes(
                    data, path_hint=f"{jar_path_str}!{member_name}"
                )
            except Exception as exc:
                warnings.warn(f"Failed to parse {jar_path_str}!{member_name}: {exc}")

    new_lang_pairs = [
        (name, lang.uuid)
        for name, lang in SLanguageBuilder.languages.items()
        if name not in existing_names
    ]
    return results, new_lang_pairs


def _register_lang_pairs(lang_pairs: list) -> None:
    from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder

    for lang_name, lang_uuid in lang_pairs:
        SLanguageBuilder.get_language(lang_name, lang_uuid)


class MpbBatchParser:
    # threshold below which a ProcessPool is not used. Spawning workers has fixed overhead of around
    # 100-200ms so serial parsing is faster for small batches.
    # threshold is exclusive so batches strictly below this count go serial.
    PARALLEL_THRESHOLD: int = 5

    def __init__(
        self,
        workers: Optional[int] = None,
        use_cache: bool = False,
        cache_load_fn: Optional[Callable[[Path], object]] = None,
        cache_save_fn: Optional[Callable[[Path, object], None]] = None,
    ):
        self._workers = workers
        self._use_cache = use_cache
        self._cache_load_fn = cache_load_fn
        self._cache_save_fn = cache_save_fn

    def parse(
        self,
        path_strings: List[str],
        pool: Optional[ProcessPoolExecutor] = None,
    ) -> Dict[str, object]:
        # parse a list of .mpb file paths returning {path_str: SModel}. This also checks ModelCache first anmd
        # then parses uncached paths either serially or in parallel depending on batch size..
        if not path_strings:
            return {}
        results: Dict[str, object] = {}
        workers = self._workers or min(os.cpu_count() or 4, 16)
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
        if pool is not None:
            future_to_path = {pool.submit(_parse_mpb_worker, ps): ps for ps in uncached}
            for future in as_completed(future_to_path):
                ps = future_to_path[future]
                try:
                    model = future.result()
                    results[ps] = model
                    self._maybe_save_cache(ps, model)
                except Exception as exc:
                    warnings.warn(f"Failed to parse {ps}: {exc}")
                    results[ps] = None
        elif workers > 1 and len(uncached) > self.PARALLEL_THRESHOLD:
            with ProcessPoolExecutor(max_workers=workers) as own_pool:
                future_to_path = {
                    own_pool.submit(_parse_mpb_worker, ps): ps for ps in uncached
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
        else:
            for ps in uncached:
                try:
                    model = _parse_mpb_worker(ps)
                    results[ps] = model
                    self._maybe_save_cache(ps, model)
                except Exception as exc:
                    warnings.warn(f"Failed to parse {ps}: {exc}")
                    results[ps] = None
        return results

    def parse_from_jars(
        self,
        jar_members: List[Tuple[str, str]],
        pool: Optional[ProcessPoolExecutor] = None,
    ) -> Dict[Tuple[str, str], object]:
        # parse .mpb members from jars hence reading bytes directly without extraction..
        # always cold: jar_mpb cache is intentionally absent so every run reads from jars and each worker
        # opens its own jar, reads bytes, parses, and returns SModel objects..
        if not jar_members:
            return {}
        workers = self._workers or min(os.cpu_count() or 4, 16)
        results: Dict[Tuple[str, str], object] = {}

        # group members by JAR so each worker handles one JAR efficiently
        by_jar: Dict[str, List[str]] = defaultdict(list)
        for jar_path_str, member_name in jar_members:
            by_jar[jar_path_str].append(member_name)

        # use caller-provided pool when available, otherwise decide serial vs own pool since serial path is used
        # when below threshold so small test projects register concepts in the main process and
        # SLanguageBuilder is correctly populated..
        if pool is not None or len(by_jar) >= self.PARALLEL_THRESHOLD:
            pool_ctx = (
                nullcontext(pool)
                if pool is not None
                else ProcessPoolExecutor(max_workers=workers)
            )
            with pool_ctx as _pool:
                futures = {
                    _pool.submit(_parse_jar_members_batch_worker, jar, members): jar
                    for jar, members in by_jar.items()
                }
                for future in as_completed(futures):
                    jar = futures[future]
                    try:
                        batch, lang_pairs = future.result()
                        for member, model in batch.items():
                            results[(jar, member)] = model
                        if lang_pairs:
                            _register_lang_pairs(lang_pairs)
                    except Exception as exc:
                        warnings.warn(f"Failed to parse JAR {jar}: {exc}")
        else:
            # serial path so parse in main process so SLanguageBuilder is populated
            for jar, members in by_jar.items():
                try:
                    batch, lang_pairs = _parse_jar_members_batch_worker(jar, members)
                    for member, model in batch.items():
                        results[(jar, member)] = model
                    if lang_pairs:
                        _register_lang_pairs(lang_pairs)
                except Exception as exc:
                    warnings.warn(f"Failed to parse JAR {jar}: {exc}")

        return results

    def _maybe_save_cache(self, path_str: str, model) -> None:
        # ssave to cache only if caching is enabled a save function is provided and the model was actually
        # parsed successfully
        if self._use_cache and self._cache_save_fn and model is not None:
            self._cache_save_fn(Path(path_str), model)
