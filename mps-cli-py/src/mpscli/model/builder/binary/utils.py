# mpscli/model/builder/binary/utils.py

import uuid
from .constants import *


def read_uuid(reader) -> str:
    head = reader.read_u64()
    tail = reader.read_u64()
    return str(uuid.UUID(int=(head << 64) | tail))


def read_string(reader) -> str:
    c = reader.read_u8()

    if c == NULL:
        return ""

    if c == STRING_INDEX:
        index = reader.read_u32()
        return reader.strings[index]

    length = reader.read_u16()
    raw = reader.read_bytes(length)
    value = raw.decode("utf-8")
    reader.strings.append(value)
    return value


def advance_until_after(reader, marker: int):
    data_len = len(reader.data)
    while reader.pos + 4 <= data_len:
        value = int.from_bytes(reader.data[reader.pos : reader.pos + 4], "big")
        if value == marker:
            reader.pos += 4
            return
        reader.pos += 1
    raise ValueError(f"Marker 0x{marker:X} not found")


def read_module_reference(reader):
    c = reader.read_u8()

    if c == NULL:
        return

    if c == MODULEREF_NAMEONLY:
        read_string(reader)
        return

    if c == MODULEREF_INDEX:
        reader.read_u32()
        return

    if c == MODULEREF_MODULEID:
        kind = reader.read_u8()
        if kind == NULL:
            return
        if kind == MODULEID_REGULAR:
            read_uuid(reader)
            return
        if kind == MODULEID_FOREIGN:
            read_string(reader)
            return

    raise ValueError(f"Unknown module reference format: 0x{c:X}")
