# mpscli/model/builder/utils/JarUtils.py
#
# Utility helpers for JAR/ZIP inspection.

import zipfile
from pathlib import Path


def jar_is_relevant(jar_path: Path) -> bool:
    # Peek inside a zip/jar to check for .msd or .mpl files without extracting.
    # Reads only the ZIP central directory (cheap - no decompression).
    # A jar is worth extracting if it contains:
    # .msd - solution descriptor
    # .mpl - language descriptor
    try:
        with zipfile.ZipFile(jar_path) as zf:
            names = zf.namelist()
            return any(name.endswith(".msd") or name.endswith(".mpl") for name in names)
    except Exception:
        return False
