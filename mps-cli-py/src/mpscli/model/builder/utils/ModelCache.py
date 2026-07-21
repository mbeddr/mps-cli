# mpscli/model/builder/utils/ModelCache.py
#
# Persistent on disk cache for parsed SModel objects.
#
# Cache key: MD5 of "<absolute path>|<mtime>|<size>" - so any file change (either content or timestamp) automatically
# invalidates its cached entry.

import hashlib
import pickle
import threading
from pathlib import Path


class ModelCache:
    # default cache directory which is ~/.mps_cli_cache so all instances share the same directory unless
    # constructed with a custom path..
    _DEFAULT_DIR: Path | None = None
    _DEFAULT_DIR_LOCK = threading.Lock()

    @classmethod
    def _default_dir(cls) -> Path:
        # lazily create the default cache directory on first use and this is actually thread-safe via a
        # class-level lock
        with cls._DEFAULT_DIR_LOCK:
            if cls._DEFAULT_DIR is None:
                d = Path.home() / ".mps_cli_cache"
                d.mkdir(exist_ok=True)
                cls._DEFAULT_DIR = d
        return cls._DEFAULT_DIR

    def __init__(self, cache_dir: Path | None = None):
        # allow a custom cache directory for testing or isolation maybe and if not provided then a
        # default ~/.mps_cli_cache dir is used
        # store None here and resolve lazily on first load\save so that constructing ModelCache or SSolutionsRepositoryBuilder
        # is safe in environments where Path.home() may raise
        self._dir = cache_dir

    def _get_dir(self) -> Path:
        # resolve the cache directory on first access so Path.home() is only called when caching is
        # actually exercised and not at construction time
        if self._dir is None:
            self._dir = self._default_dir()
        return self._dir

    def _key(self, path: Path) -> str:
        # derive a cache key from the file's absolute path, mtime, and size.
        # any change to the file produces a different key naturally invalidating the old cached entry without
        # needing an explicit invalidation step
        stat = path.stat()
        raw = f"{path}|{stat.st_mtime}|{stat.st_size}"
        return hashlib.md5(raw.encode()).hexdigest()

    def load(self, path: Path):
        # return the cached SModel for 'path' if it exists and is still valid, otherwise return None. Silently
        # swallows all errors (corrupt cache file, missing directory, etc....) since a cache miss is always
        # safe to fall back from
        try:
            key = self._key(path)
            cache_file = self._get_dir() / key
            if cache_file.exists():
                with cache_file.open("rb") as f:
                    return pickle.load(f)
        except Exception:
            pass
        return None

    def save(self, path: Path, model) -> None:
        # persist a parsed SModel to the cache
        try:
            key = self._key(path)
            cache_file = self._get_dir() / key
            with cache_file.open("wb") as f:
                pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            pass
