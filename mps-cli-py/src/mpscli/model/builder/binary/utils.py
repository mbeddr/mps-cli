# mpscli/model/builder/binary/utils.py

from mpscli.model.builder.binary.model_input_stream import ModelInputStream


def advance_until_after(reader: ModelInputStream, marker: int) -> None:
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
    return reader.read_module_ref()


def read_model_reference(reader: ModelInputStream):
    return reader.read_model_ref()
