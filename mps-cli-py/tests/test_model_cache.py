# tests/test_model_cache.py
#
# Tests for ModelCache - the persistent on-disk SModel cache. This test vovers lazy directory resolution
# and cache key derivation and load/save round-trip and safe construction in environments without a 
# resolvable home directory

import pickle
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

from mpscli.model.builder.utils.ModelCache import ModelCache
from mpscli.model.SModel import SModel


def _make_model(name="test.model", uuid="r:00000001"):
    return SModel(name, uuid, False, {})


def _make_file(tmp_dir: Path, content: bytes = b"hello") -> Path:
    f = tmp_dir / "test_file.mpb"
    f.write_bytes(content)
    return f


class TestModelCacheConstruction(unittest.TestCase):

    def test_construction_with_no_args_does_not_call_path_home(self):
        # constructing ModelCache() should never call Path.home() so that SSolutionsRepositoryBuilder() is 
        # safe in environmentss where HOME is unset
        with mock.patch("pathlib.Path.home", side_effect=RuntimeError("no home")):
            cache = ModelCache()
        # _dir should be None until first actual use
        self.assertIsNone(cache._dir)

    def test_construction_with_custom_dir_stores_it(self):
        custom = Path("/some/custom/dir")
        cache = ModelCache(cache_dir=custom)
        self.assertEqual(cache._dir, custom)

    def test_get_dir_resolves_default_on_first_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with mock.patch.object(ModelCache, "_default_dir", return_value=tmp_path):
                cache = ModelCache()
                self.assertIsNone(cache._dir)
                resolved = cache._get_dir()
                self.assertEqual(resolved, tmp_path)
                self.assertEqual(cache._dir, tmp_path)

    def test_get_dir_returns_custom_dir_without_calling_default(self):
        custom = Path("/some/custom/dir")
        cache = ModelCache(cache_dir=custom)
        with mock.patch.object(
            ModelCache,
            "_default_dir",
            side_effect=AssertionError("should not be called"),
        ):
            result = cache._get_dir()
        self.assertEqual(result, custom)


class TestModelCacheLoadAndSave(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._dir = Path(self._tmp.name)
        self._cache = ModelCache(cache_dir=self._dir)

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_returns_none_on_miss(self):
        f = _make_file(self._dir)
        result = self._cache.load(f)
        self.assertIsNone(result)

    def test_save_and_load_round_trip(self):
        f = _make_file(self._dir)
        model = _make_model()
        self._cache.save(f, model)
        loaded = self._cache.load(f)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, model.name)
        self.assertEqual(loaded.uuid, model.uuid)

    def test_load_returns_none_after_file_content_changes(self):
        f = _make_file(self._dir, content=b"original")
        model = _make_model()
        self._cache.save(f, model)
        # change file content so cache key changes so old entry is no longer found
        f.write_bytes(b"modified")
        result = self._cache.load(f)
        self.assertIsNone(result)

    def test_load_silently_returns_none_on_corrupt_cache_file(self):
        f = _make_file(self._dir)
        model = _make_model()
        self._cache.save(f, model)
        # corrupt the cache entry
        key = self._cache._key(f)
        cache_file = self._dir / key
        cache_file.write_bytes(b"not valid pickle")
        result = self._cache.load(f)
        self.assertIsNone(result)

    def test_save_does_not_raise_on_permission_error(self):
        f = _make_file(self._dir)
        model = _make_model()
        with mock.patch("builtins.open", side_effect=PermissionError("denied")):
            # should not raise and errors are silently swallowed
            self._cache.save(f, model)

    def test_load_does_not_raise_on_missing_cache_dir(self):
        cache = ModelCache(cache_dir=Path("/nonexistent/cache/dir"))
        f = _make_file(self._dir)
        result = cache.load(f)
        self.assertIsNone(result)

    def test_key_changes_when_file_content_changes(self):
        f = _make_file(self._dir, content=b"v1")
        key1 = self._cache._key(f)
        f.write_bytes(b"v2 longer content")
        key2 = self._cache._key(f)
        self.assertNotEqual(key1, key2)

    def test_key_is_deterministic(self):
        f = _make_file(self._dir)
        self.assertEqual(self._cache._key(f), self._cache._key(f))
