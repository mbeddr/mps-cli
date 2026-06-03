# mpscli/model/builder/utils/ParseCache.py
#
# Persistent per-jar cache for parsed SModel objects.
#
# Loadingg is done this way: synchronous and called explicitly after  scan_all_jars completes...
# This seems to be the only correct approach since loading too many files concurrently with
# scan_all_jars I think causes I/O competition that most likely degrades scan time significantly regardless of
# whether we cache bytes or SModel..
#
# Contents are basically SModel objects
#
# Writing works this way: non-daemon background thread so Python waits before exit
#
# Cache format explained below for per JAR entry:
# {md5}.npz - all numpy arrays for all models in this JAR, saved with np.savez() so np.load(mmap_mode='r') maps
# them directly into virtual memory without reading bytes.
# {md5}_meta.pkl - small Python objects per model: name, uuid, path, concepts_table, roles_table, prop_keys,
# ref_keys,ref_model_uuids and root_idxs.
#
# Format migration explained: if an old format file (no extension, legacy pickle) is found then it is evicted
# silently and treated as a cache miss and the next cold run rebuilds it in the new format automaticallyy..

import hashlib
import logging
import os
import pickle
import threading
import warnings
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

_log = logging.getLogger(__name__)


# arrays stored per model in the npz using m{i}_ as prefix for model index i. bytes blobs are stored as
# uint8 arrays so np.savez can handle them without setting allow_pickle=True and so they are directly memmappable..
_ARRAY_KEYS = [
    "np_concept_idxs",
    "np_role_idxs",
    "np_parent_idxs",
    "np_first_child",
    "np_next_sibling",
    "uuid_offsets",
    "uuid_data",
    "prop_start",
    "prop_key_idxs",
    "prop_val_offsets",
    "prop_val_data",
    "ref_start",
    "ref_key_idxs",
    "ref_model_idxs",
    "ref_node_uuid_offsets",
    "ref_node_uuid_data",
    "ref_resolve_offsets",
    "ref_resolve_data",
]


def _model_to_arrays(model):
    # extractt the small Python objects that cannot be stored as numpy arrays
    def as_uint8(b):
        if isinstance(b, (bytes, bytearray)):
            return np.frombuffer(b, dtype=np.uint8)
        # already numpy uint8 array
        return b

    return {
        "np_concept_idxs": model._np_concept_idxs,
        "np_role_idxs": model._np_role_idxs,
        "np_parent_idxs": model._np_parent_idxs,
        "np_first_child": model._np_first_child,
        "np_next_sibling": model._np_next_sibling,
        "uuid_offsets": model._uuid_offsets,
        "uuid_data": as_uint8(model._uuid_data),
        "prop_start": model._prop_start,
        "prop_key_idxs": model._prop_key_idxs,
        "prop_val_offsets": model._prop_val_offsets,
        "prop_val_data": as_uint8(model._prop_val_data),
        "ref_start": model._ref_start,
        "ref_key_idxs": model._ref_key_idxs,
        "ref_model_idxs": model._ref_model_idxs,
        "ref_node_uuid_offsets": model._ref_node_uuid_offsets,
        "ref_node_uuid_data": as_uint8(model._ref_node_uuid_data),
        "ref_resolve_offsets": model._ref_resolve_offsets,
        "ref_resolve_data": as_uint8(model._ref_resolve_data),
    }


def _model_meta(model, member_name):
    # extractt the small Python objects that cannot be stored as numpy arrays
    return {
        "member_name": member_name,
        "name": model.name,
        "uuid": model.uuid,
        "is_do_not_generate": model.is_do_not_generate,
        "path_to_model_file": str(model.path_to_model_file),
        "root_idxs": model._root_idxs,
        "concepts_table": model._concepts_table,
        "roles_table": model._roles_table,
        "prop_keys": model._prop_keys,
        "ref_keys": model._ref_keys,
        "ref_model_uuids": model._ref_model_uuids,
    }


def _restore_model(arrays, meta):
    # reconstruct a finalized SModel from npz arrays and pkl metadata. arrays is an NpzFile opened with
    # mmap_mode='r' so that array access is lazy I guess..
    from mpscli.model.SModel import SModel

    m = SModel.__new__(SModel)
    m.name = meta["name"]
    m.uuid = meta["uuid"]
    m.is_do_not_generate = meta["is_do_not_generate"]
    raw_path = meta.get("path_to_model_file", "")
    m.path_to_model_file = Path(raw_path) if raw_path else ""

    # building buffers are not needed after restore so mark it as finalized
    m._uuids = None
    m._concept_buf = None
    m._role_buf = None
    m._parent_buf = None
    m._properties = None
    m._references = None
    m._concepts_map = {}
    m._roles_map = {}

    # small Python objects from pkl
    m._concepts_table = meta["concepts_table"]
    m._roles_table = meta["roles_table"]
    m._prop_keys = meta["prop_keys"]
    m._ref_keys = meta["ref_keys"]
    m._ref_model_uuids = meta["ref_model_uuids"]
    m._root_idxs = meta["root_idxs"]

    # lazy caches so not serialized
    m._node_cache = {}
    m._uuid_index = None
    m._prop_key_lookup = None
    m._ref_key_lookup = None

    # numpy arrays from npz (these are mmaped on warm load so no bytes read yet)
    m._np_concept_idxs = arrays["np_concept_idxs"]
    m._np_role_idxs = arrays["np_role_idxs"]
    m._np_parent_idxs = arrays["np_parent_idxs"]
    m._np_first_child = arrays["np_first_child"]
    m._np_next_sibling = arrays["np_next_sibling"]
    m._uuid_offsets = arrays["uuid_offsets"]
    m._uuid_data = arrays["uuid_data"]
    m._prop_start = arrays["prop_start"]
    m._prop_key_idxs = arrays["prop_key_idxs"]
    m._prop_val_offsets = arrays["prop_val_offsets"]
    m._prop_val_data = arrays["prop_val_data"]
    m._ref_start = arrays["ref_start"]
    m._ref_key_idxs = arrays["ref_key_idxs"]
    m._ref_model_idxs = arrays["ref_model_idxs"]
    m._ref_node_uuid_offsets = arrays["ref_node_uuid_offsets"]
    m._ref_node_uuid_data = arrays["ref_node_uuid_data"]
    m._ref_resolve_offsets = arrays["ref_resolve_offsets"]
    m._ref_resolve_data = arrays["ref_resolve_data"]

    m._finalized = True
    m._build_root_nodes()
    return m


class _FileCache:

    def __init__(self, cache_dir: Path, workers: int):
        self._dir = cache_dir
        self._workers = workers
        self._data: Dict[str, dict] = {}
        self._dirty: Dict[str, Tuple[float, int, dict]] = {}
        self._lock = threading.Lock()
        self._dir.mkdir(parents=True, exist_ok=True)

    def _npz_path(self, jar_path_str: str) -> Path:
        return self._dir / (hashlib.md5(jar_path_str.encode()).hexdigest() + ".npz")

    def _meta_path(self, jar_path_str: str) -> Path:
        return self._dir / (
            hashlib.md5(jar_path_str.encode()).hexdigest() + "_meta.pkl"
        )

    def _load_one(
        self, meta_file: Path, jar_stats: Dict[str, Tuple[float, int]]
    ) -> Optional[Tuple[str, dict]]:
        # load one jar's cached models from npz + pkl pair. npz is memory-mapped so arrays are nott read into RAM
        # until first access and warm cache_load could most likely be instant I guess..
        npz_file = meta_file.with_name(meta_file.name.replace("_meta.pkl", ".npz"))
        if not npz_file.exists():
            # meta without npz means incomplete write so remove
            try:
                meta_file.unlink()
            except FileNotFoundError:
                pass
            return None
        try:
            with meta_file.open("rb") as f:
                entry = pickle.load(f)
            jar_path_str = entry.get("jar_path_str", "")
            if not jar_path_str:
                return None
            stored_mtime = entry.get("mtime")
            stored_size = entry.get("size")
            if stored_mtime is None or stored_size is None:
                try:
                    meta_file.unlink()
                except FileNotFoundError:
                    pass
                try:
                    npz_file.unlink()
                except FileNotFoundError:
                    pass
                return None
            current = jar_stats.get(jar_path_str)
            if current is None:
                # jar no longer in scan so remove..
                try:
                    meta_file.unlink()
                except FileNotFoundError:
                    pass
                try:
                    npz_file.unlink()
                except FileNotFoundError:
                    pass
                return None
            cur_mtime, cur_size = current
            if stored_mtime != cur_mtime or stored_size != cur_size:
                # jar is rebuilt so remove any possible stale entries
                try:
                    meta_file.unlink()
                except FileNotFoundError:
                    pass
                try:
                    npz_file.unlink()
                except FileNotFoundError:
                    pass
                return None

            # mmap the npz so most likely no bytes read until arrays are actually accessed..
            # this mmap concept is really awesome!
            npz = np.load(str(npz_file), mmap_mode="r", allow_pickle=False)
            content = {}
            for i, model_meta in enumerate(entry["models"]):
                prefix = f"m{i}_"
                model_arrays = {k: npz[prefix + k] for k in _ARRAY_KEYS}
                content[model_meta["member_name"]] = _restore_model(
                    model_arrays, model_meta
                )
            return jar_path_str, content
        except Exception:
            return None

    def load_sync(self, jar_stats: Dict[str, Tuple[float, int]]) -> None:
        # synchronous parallel load called after scan_all_jars so no I/O competition with scan and also
        # no GIL competition likely from concurrent threads
        meta_files = [
            f
            for f in self._dir.iterdir()
            if f.is_file() and f.name.endswith("_meta.pkl")
        ]
        # remove legacy format files (no extension and old pickle-only cache formatss)
        for f in self._dir.iterdir():
            if f.is_file() and f.suffix == "" and not f.name.endswith("_meta"):
                try:
                    f.unlink()
                except FileNotFoundError:
                    pass
        if not meta_files:
            return
        from concurrent.futures import ThreadPoolExecutor

        loaded = 0
        with ThreadPoolExecutor(max_workers=self._workers) as pool:
            for result in pool.map(
                lambda mf: self._load_one(mf, jar_stats), meta_files
            ):
                if result is not None:
                    jar_path_str, content = result
                    self._data[jar_path_str] = content
                    loaded += 1
        if loaded:
            _log.info(
                "[cache] loaded %d/%d entries from %s",
                loaded,
                len(meta_files),
                self._dir.name,
            )

    def get(self, jar_path_str: str) -> Optional[dict]:
        return self._data.get(jar_path_str)

    def put_many(
        self,
        jar_map: Dict[str, dict],
        jar_stats: Optional[Dict[str, Tuple[float, int]]] = None,
    ) -> None:
        with self._lock:
            for jar_path_str, content in jar_map.items():
                self._data[jar_path_str] = content
                if jar_stats:
                    stats = jar_stats.get(jar_path_str)
                    if stats:
                        mtime, size = stats
                        self._dirty[jar_path_str] = (mtime, size, content)

    def _save_all(self, to_write: Dict) -> None:
        from timeit import default_timer as timer

        t0 = timer()
        for jar_path_str, (mtime, size, content) in to_write.items():
            try:
                # [(member_name, SModel)]
                models = list(content.items())
                # build combined npz dict with m{i}_ prefixed array names
                npz_data = {}
                models_meta = []
                for i, (member_name, model) in enumerate(models):
                    prefix = f"m{i}_"
                    for k, v in _model_to_arrays(model).items():
                        npz_data[prefix + k] = v
                    models_meta.append(_model_meta(model, member_name))
                npz_path = self._npz_path(jar_path_str)
                meta_path = self._meta_path(jar_path_str)
                # write npz first and in case if interrupted then I think meta load will fail because _load_one
                # checks npz existence first and np.savez appends .npz to names that do not already end in .npz and
                # also use _tmp.npz as the temp name so the rename is mostly not ambiguous on Windows..
                tmp_npz = npz_path.with_name(npz_path.stem + "_tmp.npz")
                np.savez(str(tmp_npz), **npz_data)
                tmp_npz.replace(npz_path)
                # write meta pkl
                entry = {
                    "jar_path_str": jar_path_str,
                    "mtime": mtime,
                    "size": size,
                    "models": models_meta,
                }
                tmp_meta = meta_path.with_name(meta_path.stem + "_tmp.pkl")
                with tmp_meta.open("wb") as f:
                    pickle.dump(entry, f, protocol=pickle.HIGHEST_PROTOCOL)
                tmp_meta.replace(meta_path)
            except Exception as exc:
                warnings.warn(f"Cache save failed for {jar_path_str}: {exc}")
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
        self._mpb = _FileCache(self._CACHE_ROOT / "jar_mpb", w)
        self._xml = _FileCache(self._CACHE_ROOT / "jar_xml", w)

    def load_sync(self, jar_stats: Dict[str, Tuple[float, int]]) -> None:
        # call once after scan_all_jars, this validates staleness using jar_stats
        self._mpb.load_sync(jar_stats)
        self._xml.load_sync(jar_stats)

    def get_mpb(self, jar_path_str: str) -> Optional[dict]:
        return self._mpb.get(jar_path_str)

    def put_mpb_many(
        self,
        jar_map: Dict[str, dict],
        jar_stats: Optional[Dict[str, Tuple[float, int]]] = None,
    ) -> None:
        self._mpb.put_many(jar_map, jar_stats)

    def get_xml(self, jar_path_str: str) -> Optional[dict]:
        return self._xml.get(jar_path_str)

    def put_xml_many(
        self,
        jar_map: Dict[str, dict],
        jar_stats: Optional[Dict[str, Tuple[float, int]]] = None,
    ) -> None:
        self._xml.put_many(jar_map, jar_stats)

    def flush(self) -> None:
        self._mpb.flush()
        self._xml.flush()

    def stats(self) -> dict:
        def dir_stats(d: Path) -> dict:
            if not d.exists():
                return {"entries": 0, "size_mb": 0.0}
            files = list(d.iterdir())
            size = sum(f.stat().st_size for f in files if f.is_file())
            return {"entries": len(files), "size_mb": round(size / 1024 / 1024, 1)}

        return {
            "jar_mpb": dir_stats(self._CACHE_ROOT / "jar_mpb"),
            "jar_xml": dir_stats(self._CACHE_ROOT / "jar_xml"),
        }
