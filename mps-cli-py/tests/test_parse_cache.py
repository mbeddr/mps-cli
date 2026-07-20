# tests/test_parse_cache.py
#
# Tests for ParseCache specifically the persistent SModel cache used by phase3 (disk_solutions) and phase4 (jar_xml). 
# Verifies save/load round-trips and mtime+size staleness evictionn, lang_pairs storagee and re-registration and 
# atomic write behaviour..

import pickle
import tempfile
import unittest
import warnings
from pathlib import Path

from mpscli.model.SModel import SModel
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder
from mpscli.model.builder.utils.ParseCache import _FileCache, ParseCache


def _make_model(name="test.model", uuid="r:00000001"):
    return SModel(name, uuid, False, {})


def _make_stats(path_str, mtime=1000.0, size=512):
    return {path_str: (mtime, size)}


class TestFileCacheSaveAndLoad(unittest.TestCase):

    def setUp(self):
        SLanguageBuilder.languages = {}
        self._tmp = tempfile.TemporaryDirectory()
        self._dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_empty_cache_load_does_not_raise(self):
        cache = _FileCache(self._dir / "sub", workers=1)
        # should complete without error even when directoryy does not existt
        cache.load_sync({})

    def test_put_and_get_returns_models(self):
        cache = _FileCache(self._dir, workers=1)
        model = _make_model()
        jar = "fake/path.jar"
        cache.put_many({jar: {("fpr", "models/foo"): model}}, stats=_make_stats(jar))
        result = cache.get(jar)
        self.assertIsNotNone(result)
        self.assertIn(("fpr", "models/foo"), result)

    def test_save_and_load_round_trip(self):
        cache = _FileCache(self._dir, workers=1)
        model = _make_model()
        jar = "fake/path.jar"
        stats = _make_stats(jar)
        cache.put_many({jar: {("fpr", "x"): model}}, stats=stats)
        cache._save_all(dict(cache._dirty))

        # reload in a fresh cache instance
        cache2 = _FileCache(self._dir, workers=1)
        cache2.load_sync(stats)
        result = cache2.get(jar)
        self.assertIsNotNone(result)
        self.assertIn(("fpr", "x"), result)

    def test_stale_entry_evicted_on_mtime_change(self):
        cache = _FileCache(self._dir, workers=1)
        model = _make_model()
        jar = "fake/path.jar"
        cache.put_many(
            {jar: {("fpr", "x"): model}}, stats=_make_stats(jar, mtime=1000.0)
        )
        cache._save_all(dict(cache._dirty))

        # reload with different mtime so entry should be basically be evicted...
        cache2 = _FileCache(self._dir, workers=1)
        cache2.load_sync(_make_stats(jar, mtime=9999.0))
        self.assertIsNone(cache2.get(jar))
        # pkl file should have been deleted
        self.assertEqual(list(self._dir.glob("*.pkl")), [])

    def test_stale_entry_evicted_on_size_change(self):
        cache = _FileCache(self._dir, workers=1)
        model = _make_model()
        jar = "fake/path.jar"
        cache.put_many({jar: {("fpr", "x"): model}}, stats=_make_stats(jar, size=512))
        cache._save_all(dict(cache._dirty))

        cache2 = _FileCache(self._dir, workers=1)
        cache2.load_sync(_make_stats(jar, size=999))
        self.assertIsNone(cache2.get(jar))

    def test_entry_evicted_when_jar_not_in_scan(self):
        cache = _FileCache(self._dir, workers=1)
        jar = "fake/path.jar"
        cache.put_many({jar: {}}, stats=_make_stats(jar))
        cache._save_all(dict(cache._dirty))

        # reload with empty stats so jar no longer in scan
        cache2 = _FileCache(self._dir, workers=1)
        cache2.load_sync({})
        self.assertIsNone(cache2.get(jar))
        self.assertEqual(list(self._dir.glob("*.pkl")), [])

    def test_corrupt_pkl_evicted_silently(self):
        cache = _FileCache(self._dir, workers=1)
        pkl = self._dir / "corrupt.pkl"
        pkl.write_bytes(b"not valid pickle data")
        with warnings.catch_warnings(record=True):
            cache.load_sync({"anything": (1.0, 1)})
        self.assertFalse(pkl.exists())

    def test_atomic_write_leaves_no_tmp_files(self):
        cache = _FileCache(self._dir, workers=1)
        model = _make_model()
        jar = "fake/path.jar"
        cache.put_many({jar: {("fpr", "x"): model}}, stats=_make_stats(jar))
        cache._save_all(dict(cache._dirty))
        tmp_files = list(self._dir.glob("*_tmp.pkl"))
        self.assertEqual(tmp_files, [])

    def test_lang_pairs_stored_and_reregistered_on_load(self):
        SLanguageBuilder.languages = {}
        cache = _FileCache(self._dir, workers=1)
        model = _make_model()
        jar = "fake/path.jar"
        lang_pairs = [("my.test.language", "uuid-1234")]
        cache.put_many(
            {jar: {("fpr", "x"): model}},
            stats=_make_stats(jar),
            lang_pairs_map={jar: lang_pairs},
        )
        cache._save_all(dict(cache._dirty))

        # clear languages and reload and they should be re-registered from cache
        SLanguageBuilder.languages = {}
        cache2 = _FileCache(self._dir, workers=1)
        cache2.load_sync(_make_stats(jar))
        self.assertIn("my.test.language", SLanguageBuilder.languages)

    def test_missing_lang_pairs_in_old_entry_handled_gracefully(self):
        # simulate an older cache entry written before lang_pairs was added
        cache = _FileCache(self._dir, workers=1)
        jar = "fake/path.jar"
        mtime, size = 1000.0, 512
        pkl_path = cache._pkl_path(jar)
        # write entry without lang_pairs key
        entry = {
            "path_str": jar,
            "mtime": mtime,
            "size": size,
            "models": {("fpr", "x"): _make_model()},
        }
        with pkl_path.open("wb") as f:
            pickle.dump(entry, f, protocol=pickle.HIGHEST_PROTOCOL)

        cache2 = _FileCache(self._dir, workers=1)
        # should load without error and return models
        cache2.load_sync(_make_stats(jar, mtime=mtime, size=size))
        self.assertIsNotNone(cache2.get(jar))

    def test_bad_entry_in_save_does_not_stop_others(self):
        cache = _FileCache(self._dir, workers=1)
        model = _make_model()
        good_jar = "fake/good.jar"
        to_write = {
            good_jar: (1000.0, 512, {("fpr", "x"): model}, []),
            # None key will fail md5 encoding
            None: (0.0, 0, {}, []),
        }
        with warnings.catch_warnings(record=True):
            cache._save_all(to_write)
        # good jar should still have been saved
        good_pkl = cache._pkl_path(good_jar)
        self.assertTrue(good_pkl.exists())


class TestParseCachePublicApi(unittest.TestCase):

    def setUp(self):
        SLanguageBuilder.languages = {}
        self._tmp = tempfile.TemporaryDirectory()
        self._cache_root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _make_cache(self):
        cache = ParseCache(workers=1)
        # override cache root to use temp dir
        from mpscli.model.builder.utils.ParseCache import _FileCache

        cache._xml = _FileCache(self._cache_root / "jar_xml", 1)
        cache._disk = _FileCache(self._cache_root / "disk_solutions", 1)
        return cache

    def test_get_xml_returns_none_on_miss(self):
        cache = self._make_cache()
        self.assertIsNone(cache.get_xml("not/there.jar"))

    def test_get_disk_returns_none_on_miss(self):
        cache = self._make_cache()
        self.assertIsNone(cache.get_disk("not/there.msd"))

    def test_put_and_get_xml(self):
        cache = self._make_cache()
        jar = "some/jar.jar"
        model = _make_model()
        cache.put_xml_many({jar: {("fpr", "x"): model}}, jar_stats=_make_stats(jar))
        result = cache.get_xml(jar)
        self.assertIsNotNone(result)

    def test_put_and_get_disk(self):
        cache = self._make_cache()
        msd = "some/solution.msd"
        model = _make_model()
        cache.put_disk_many({msd: {"model.mps": model}}, msd_stats=_make_stats(msd))
        result = cache.get_disk(msd)
        self.assertIsNotNone(result)

    def test_flush_creates_pkl_files(self):
        cache = self._make_cache()
        jar = "some/jar.jar"
        model = _make_model()
        cache.put_xml_many({jar: {("fpr", "x"): model}}, jar_stats=_make_stats(jar))
        # force synchronouss save by calling _save_all directly
        (self._cache_root / "jar_xml").mkdir(parents=True, exist_ok=True)
        cache._xml._save_all(dict(cache._xml._dirty))
        pkl_files = list((self._cache_root / "jar_xml").glob("*.pkl"))
        self.assertEqual(len(pkl_files), 1)

    def test_stats_returns_counts(self):
        cache = self._make_cache()
        stats = cache.stats()
        self.assertIn("jar_xml", stats)
        self.assertIn("disk_solutions", stats)
        self.assertEqual(stats["jar_xml"]["entries"], 0)

    def test_load_sync_with_no_dir_does_not_raise(self):
        cache = self._make_cache()
        # should complete without error when directories do not exist yet
        cache.load_sync({"fake/jar.jar": (1.0, 100)})
        cache.load_disk_sync({"fake/sol.msd": (1.0, 100)})
