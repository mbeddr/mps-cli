import time
import unittest

from mpscli.model.builder.SModelBuilderBinaryPersistency import (
    SModelBuilderBinaryPersistency,
)

MPB = (
    "../mps_test_projects/"
    "mps_cli_binary_persistency_generated_low_level_access_test_data/"
    "mps.cli.lanuse.library_top.binary_persistency.authors_top.mpb"
)


class TestParserPerformance(unittest.TestCase):
    def test_single_file_parse_under_2s(self):
        t0 = time.perf_counter()
        SModelBuilderBinaryPersistency().build(MPB)
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 2.0, f"Parsing took {elapsed:.2f}s, limit is 2s")
