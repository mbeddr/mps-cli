"""
parallel_build.py — This lets us build models in parallel instead of one-by-one.

Just replace the old loop (in SSolutionBuilder) with this:

    from parallel_build import build_models_parallel
    models = build_models_parallel(model_paths)

It uses separate processes to get around Python's speed limits (the GIL), so it's much faster.

Don't worry about data leaking between models since each worker starts with a fresh builder for every file it handles.
"""

from __future__ import annotations

import os
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Optional


# worker function (runs in subprocess)
def _parse_one(path: str):
    """
    Parse a single .mpb file.  Runs in a worker process.
    Returns the SModel object, or raises on hard failure.
    """
    # import here so each worker process gets a fresh module state
    from mpscli.model.builder.SModelBuilderBinaryPersistency import (
        SModelBuilderBinaryPersistency,
    )

    builder = SModelBuilderBinaryPersistency()
    return builder.build(path)


def build_models_parallel(
    paths: List[str],
    workers: Optional[int] = None,
    show_progress: bool = True,
) -> List:
    """
    Parse all .mpb files in paths using a process pool.

    This returns a list of SModel objects in the same order as paths and failed files are returned as None (nevertheless a warning is printed).

    Parameters:
    paths: list of absolute paths to .mpb files
    workers: number of worker processes (None means auto)
    show_progress: print a one line status per completed file
    """
    if not paths:
        return []

    # limit workers- I/O bound on small files and CPU bound on large ones
    if workers is None:
        workers = min(os.cpu_count() or 4, 16)

    results = [None] * len(paths)
    index_of = {p: i for i, p in enumerate(paths)}

    with ProcessPoolExecutor(max_workers=workers) as pool:
        future_to_path = {pool.submit(_parse_one, p): p for p in paths}

        done = 0
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            done += 1
            try:
                model = future.result()
                results[index_of[path]] = model
                if show_progress:
                    name = os.path.basename(path)
                    print(f"[{done}/{len(paths)}] OK  {name}")
            except Exception:
                if show_progress:
                    name = os.path.basename(path)
                    print(f"[{done}/{len(paths)}] ERR {name}")
                    traceback.print_exc()

    return results
