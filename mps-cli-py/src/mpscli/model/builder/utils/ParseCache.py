# mpscli/model/builder/utils/ParseCache.py
#
# Persistent cache for parsed SModel objects from JAR FPR/MPS and disk FPR/MPS parsing.
#
# Loading is done synchronously after scan_all_jars completes. This seems to be the only correct approach 
# since loading concurrently with scan_all_jars I think causes I/O competition that degrades scan 
# time regardless of whether we cache bytes or SModel
#
# Contents are SModel objects, pickled per jar or per .msd file.
#
# Writing works via a non-daemon background thread so Python waits before exit..
#
# Two caches are maintained:
#   jar_xml        - SModel objects for JAR FPR/MPS parsing (phase4) and keyedd on JAR mtime+size.
#   disk_solutions - SModel objects for disk FPR/MPS parsing (phase3) and keyed on .msd mtime+size
#
# jar_mpb (binary .mpb parsing, phase2) is intentionally not cached here because on local disk re-parsing .mpb 
# files from jars via ProcessPool takes arpund 90s which is faster than any serialization/deserialization 
# approach for around 5500 models involved. The jar I/O is fast on local disk and the parse compute is fully 
# parallelized across workers
#
# Cache format per entry:
# {md5}.pkl - a dict containing path_str, mtime, size, models dict and lang_pairs list and validated against 
# mtime+size on load so the lang_pairs are re-registered on load so registry-only languages (seen during parsing 
# but not in MPB workers) are correctly restored on warm runs.
#
# Also if an unrecognised or corrupt file is found it is silently removed and treated as a cache miss and 
# the next cold run rebuilds it automatically

import hashlib
import logging
import os
import pickle
import threading
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_log = logging.getLogger(__name__)


class _FileCache:

    def __init__(self, cache_dir: Path, workers: int):
        self._dir = cache_dir
        self._workers = workers
        self._data: Dict[str, dict] = {}
        self._dirty: Dict[str, Tuple[float, int, dict, list]] = {}
        self._lock = threading.Lock()
        # lazy directory creation so only created on first write and not on construction
        self._dir_created = False

    def _ensure_dir(self) -> None:
        if not self._dir_created:
            self._dir.mkdir(parents=True, exist_ok=True)
            self._dir_created = True

    def _pkl_path(self, path_str: str) -> Path:
        return self._dir / (hashlib.md5(path_str.encode()).hexdigest() + ".pkl")

    def _load_one(
        self, pkl_file: Path, stats: Dict[str, Tuple[float, int]]
    ) -> Optional[Tuple[str, dict, list]]:
        # load one entry from pkl and this validates mtime+size before returning and 
        # returns (path_str, models, lang_pairs) or None on miss/errorr
        try:
            with pkl_file.open("rb") as f:
                entry = pickle.load(f)
            path_str = entry.get("path_str", "")
            if not path_str:
                return None
            stored_mtime = entry.get("mtime")
            stored_size = entry.get("size")
            if stored_mtime is None or stored_size is None:
                try:
                    pkl_file.unlink()
                except FileNotFoundError:
                    pass
                return None
            current = stats.get(path_str)
            if current is None:
                # path no longer in scan so remove
                try:
                    pkl_file.unlink()
                except FileNotFoundError:
                    pass
                return None
            cur_mtime, cur_size = current
            if stored_mtime != cur_mtime or stored_size != cur_size:
                # file has changed since we cached it so remove
                try:
                    pkl_file.unlink()
                except FileNotFoundError:
                    pass
                return None
            models = entry.get("models", {})
            # lang_pairs mayy be absent in older cache entries so treated as empty list
            lang_pairs = entry.get("lang_pairs", [])
            return path_str, models, lang_pairs
        except Exception:
            # corrupt or unrecognised format so remove silently
            try:
                pkl_file.unlink()
            except FileNotFoundError:
                pass
            return None

    def load_sync(self, stats: Dict[str, Tuple[float, int]]) -> None:
        # synchronous load called after scan so no io competition with scan and also re-registers 
        # lang_pairs so registry-only languages are restored on warm runs..
        if not self._dir.exists():
            return
        pkl_files = [
            f for f in self._dir.iterdir() if f.is_file() and f.name.endswith(".pkl")
        ]
        if not pkl_files:
            return
        from concurrent.futures import ThreadPoolExecutor
        from mpscli.model.builder.utils.MpbBatchParser import _register_lang_pairs

        loaded = 0
        with ThreadPoolExecutor(max_workers=self._workers) as pool:
            for result in pool.map(lambda pf: self._load_one(pf, stats), pkl_files):
                if result is not None:
                    path_str, models, lang_pairs = result
                    self._data[path_str] = models
                    if lang_pairs:
                        _register_lang_pairs(lang_pairs)
                    loaded += 1
        if loaded:
            _log.info(
                "[cache] loaded %d/%d entries from %s",
                loaded,
                len(pkl_files),
                self._dir.name,
            )

    def get(self, path_str: str) -> Optional[dict]:
        return self._data.get(path_str)

    def put_many(
        self,
        entry_map: Dict[str, dict],
        stats: Optional[Dict[str, Tuple[float, int]]] = None,
        lang_pairs_map: Optional[Dict[str, list]] = None,
    ) -> None:
        with self._lock:
            for path_str, models in entry_map.items():
                self._data[path_str] = models
                if stats:
                    s = stats.get(path_str)
                    if s:
                        mtime, size = s
                        lp = lang_pairs_map.get(path_str, []) if lang_pairs_map else []
                        self._dirty[path_str] = (mtime, size, models, lp)

    def _save_all(self, to_write: Dict) -> None:
        from timeit import default_timer as timer

        self._ensure_dir()
        t0 = timer()
        for path_str, (mtime, size, models, lang_pairs) in to_write.items():
            try:
                entry = {
                    "path_str": path_str,
                    "mtime": mtime,
                    "size": size,
                    "models": models,
                    "lang_pairs": lang_pairs,
                }
                pkl_path = self._pkl_path(path_str)
                # atomic write via temp file then rename so an interrupted save never leaves a partial cache entry 
                # that looks valid
                tmp_path = pkl_path.with_name(pkl_path.stem + "_tmp.pkl")
                with tmp_path.open("wb") as f:
                    pickle.dump(entry, f, protocol=pickle.HIGHEST_PROTOCOL)
                tmp_path.replace(pkl_path)
            except Exception as exc:
                warnings.warn(f"Cache save failed for {path_str}: {exc}")
        _log.info(
            "[cache] saved %d entries to %s in %.1fs",
            len(to_write),
            self._dir.name,
            timer() - t0,
        )

    def flush(self) -> None:
        with self._lock:
            to_write = dict(self._dirty)
            self._dirty.clear()
        if not to_write:
            return
        _log.info("[cache] saving %d entries to %s...", len(to_write), self._dir.name)
        threading.Thread(
            target=self._save_all,
            args=(to_write,),
            daemon=False,
            name="cache-flush",
        ).start()


class ParseCache:
    _CACHE_ROOT = Path.home() / ".mps_cli_cache"

    def __init__(self, workers: int = None):
        w = workers or min(os.cpu_count() or 4, 16)
        self._xml = _FileCache(self._CACHE_ROOT / "jar_xml", w)
        self._disk = _FileCache(self._CACHE_ROOT / "disk_solutions", w)

    def load_sync(self, jar_stats: Dict[str, Tuple[float, int]]) -> None:
        # call once after scan_all_jars and this validates staleness using jar mtime+size
        self._xml.load_sync(jar_stats)

    def load_disk_sync(self, msd_stats: Dict[str, Tuple[float, int]]) -> None:
        # call once before disk phase and this validates staleness using msd mtime+size
        self._disk.load_sync(msd_stats)

    def get_xml(self, jar_path_str: str) -> Optional[dict]:
        return self._xml.get(jar_path_str)

    def put_xml_many(
        self,
        jar_map: Dict[str, dict],
        jar_stats: Optional[Dict[str, Tuple[float, int]]] = None,
        lang_pairs_map: Optional[Dict[str, list]] = None,
    ) -> None:
        self._xml.put_many(jar_map, jar_stats, lang_pairs_map)

    def get_disk(self, msd_path_str: str) -> Optional[dict]:
        return self._disk.get(msd_path_str)

    def put_disk_many(
        self,
        msd_map: Dict[str, dict],
        msd_stats: Optional[Dict[str, Tuple[float, int]]] = None,
        lang_pairs_map: Optional[Dict[str, list]] = None,
    ) -> None:
        self._disk.put_many(msd_map, msd_stats, lang_pairs_map)

    def flush(self) -> None:
        self._xml.flush()
        self._disk.flush()

    def stats(self) -> dict:
        def dir_stats(d: Path) -> dict:
            if not d.exists():
                return {"entries": 0, "size_mb": 0.0}
            files = list(d.iterdir())
            size = sum(f.stat().st_size for f in files if f.is_file())
            return {"entries": len(files), "size_mb": round(size / 1024 / 1024, 1)}

        return {
            "jar_xml": dir_stats(self._CACHE_ROOT / "jar_xml"),
            "disk_solutions": dir_stats(self._CACHE_ROOT / "disk_solutions"),
        }
