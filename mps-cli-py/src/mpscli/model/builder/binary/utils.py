# mpscli/model/builder/binary/utils.py
#
# Utility helpers. All module/model ref reading delegates to ModelInputStream
# methods so there is exactly one implementation.

from mpscli.model.builder.binary.model_input_stream import ModelInputStream


def advance_until_after(reader: ModelInputStream, marker: int) -> None:
    """
    Sliding-window scan: advance until `marker` (4-byte big-endian int) is
    found and consumed. Safe — no seek-back, no risk of infinite loops.

    WARNING: this does NOT call read_string(), so the string table will NOT
    be populated for any strings encountered during the scan.  Only use this
    for sections where string table correctness is not required (e.g. finding
    HEADER_END before the string table matters).
    """
    data = reader.data
    target = marker.to_bytes(4, "big")
    start = reader.pos

    while reader.pos + 4 <= len(data):
        if data[reader.pos : reader.pos + 4] == target:
            reader.pos += 4
            return
        reader.pos += 1

    raise RuntimeError(f"Marker 0x{marker:08X} not found scanning from pos {start}")


def read_module_reference(reader: ModelInputStream):
    """Delegates to ModelInputStream.read_module_ref() — single canonical impl."""
    return reader.read_module_ref()


def read_model_reference(reader: ModelInputStream):
    """Delegates to ModelInputStream.read_model_ref() — single canonical impl."""
    return reader.read_model_ref()
