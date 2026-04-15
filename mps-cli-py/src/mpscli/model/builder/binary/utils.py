# mpscli/model/builder/binary/utils.py
#
# Utility helpers for the binary persistence parser. These are just thin wrappers and a recovery helper so
# they have no direct Java equivalents and also Java's BinaryPersistence raises ModelReadException on any parse
# failure rather than attempting recovery.

from mpscli.model.builder.binary.model_input_stream import ModelInputStream


def advance_until_after(reader: ModelInputStream, marker: int) -> None:
    # brute-force byte scan that advances the stream position to immediately after the first occurrence of the
    # given 4-byte big-endian marker value..
    # There is no Java equivalent since Java's BinaryPersistence throws ModelReadException and aborts loading
    # entirely on any unknown format but our Python opts for lenient partial extraction. The node tree is usually I think
    # intact even when an unusual import reference encoding is encountered so partial results are better
    # than no results
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
    # thin wrapper around ModelInputStream.read_module_ref().
    # Exists only so module_refs.py and other callers in the binary package can import a named function rather than
    # coupling directly to ModelInputStream. This also makes the call sites more readable I thinkk  so basically
    # "read_module_reference(reader)" is clearer than "reader.read_module_ref()" in the context where the
    # reader type is implicit..
    return reader.read_module_ref()
