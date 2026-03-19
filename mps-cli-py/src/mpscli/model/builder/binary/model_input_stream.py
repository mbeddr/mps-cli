import struct


class ModelInputStream:
    STREAM_ID_V1 = 0x00000300
    STREAM_ID_V2 = 0x00000400
    STREAM_ID_V3 = 0x00000500

    STUB_NONE = 0x12
    STUB_ID = 0x13

    HEADER_START = 0x91ABABA9
    HEADER_END = 0xABABABAB
    REGISTRY_START = 0x5A5A5A5A
    REGISTRY_END = 0xA5A5A5A5
    MODEL_START = 0xBABABABA
    HEADER_ATTRIBUTES = 0x7E
    DEPENDENCY_V1 = 0x01

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.string_table: list = []

    def tell(self) -> int:
        return self.pos

    def seek(self, pos: int):
        self.pos = pos

    def read_u8(self) -> int:
        if self.pos >= len(self.data):
            raise RuntimeError(f"read_u8: EOF at pos {self.pos}")
        v = self.data[self.pos]
        self.pos += 1
        return v

    def peek_u8(self) -> int:
        # return the next byte without advancing the read position
        if self.pos >= len(self.data):
            raise RuntimeError(f"peek_u8: EOF at pos {self.pos}")
        return self.data[self.pos]

    def read_bool(self) -> bool:
        return self.read_u8() != 0

    def read_u16(self) -> int:
        if self.pos + 2 > len(self.data):
            raise RuntimeError(f"read_u16: EOF at pos {self.pos}")
        v = struct.unpack_from(">H", self.data, self.pos)[0]
        self.pos += 2
        return v

    def read_i16(self) -> int:
        if self.pos + 2 > len(self.data):
            raise RuntimeError(f"read_i16: EOF at pos {self.pos}")
        v = struct.unpack_from(">h", self.data, self.pos)[0]
        self.pos += 2
        return v

    def read_u32(self) -> int:
        if self.pos + 4 > len(self.data):
            raise RuntimeError(f"read_u32: EOF at pos {self.pos}")
        v = struct.unpack_from(">I", self.data, self.pos)[0]
        self.pos += 4
        return v

    def read_i32(self) -> int:
        if self.pos + 4 > len(self.data):
            raise RuntimeError(f"read_i32: EOF at pos {self.pos}")
        v = struct.unpack_from(">i", self.data, self.pos)[0]
        self.pos += 4
        return v

    def read_u64(self) -> int:
        if self.pos + 8 > len(self.data):
            raise RuntimeError(f"read_u64: EOF at pos {self.pos}")
        v = struct.unpack_from(">Q", self.data, self.pos)[0]
        self.pos += 8
        return v

    def read_bytes(self, length: int) -> bytes:
        if self.pos + length > len(self.data):
            raise RuntimeError(
                f"read_bytes({length}): EOF at pos {self.pos}, "
                f"only {len(self.data) - self.pos} bytes left"
            )
        v = self.data[self.pos : self.pos + length]
        self.pos += length
        return v

    # UUID (two big-endian long which is same as Java writeUUID/readUUID)
    def read_uuid(self) -> tuple:
        high = self.read_u64()
        low = self.read_u64()
        return (high, low)

    def read_string(self):
        c = self.read_u8()

        if c == 0x70:
            return None

        if c == 0x01:
            index = self.read_u32()
            if index >= len(self.string_table):
                raise RuntimeError(
                    f"String table index {index} out of range "
                    f"(table size={len(self.string_table)}) at pos {self.pos}"
                )
            return self.string_table[index]

        length = self.read_u16()
        raw = self.read_bytes(length)
        s = raw.decode("utf-8", errors="replace")
        self.string_table.append(s)
        return s

    def read_module_ref(self):
        kind = self.read_u8()

        if kind == 0x70:
            return None

        if kind == 0x18:
            return {"type": "name_only", "name": self.read_string()}

        if kind == 0x19:
            return {"type": "indexed", "index": self.read_u32()}

        if kind == 0x17:
            sub = self.read_u8()
            if sub == 0x70:
                module_id = None
            elif sub == 0x48:
                module_id = self.read_uuid()
            elif sub == 0x47:
                module_id = self.read_string()
            else:
                raise RuntimeError(
                    f"Unknown module id sub-type 0x{sub:02X} at pos {self.pos}"
                )
            name = self.read_string()
            return {"type": "full", "id": module_id, "name": name}

        raise RuntimeError(f"Unknown module ref kind 0x{kind:02X} at pos {self.pos}")

    def read_model_ref(self):
        kind = self.read_u8()

        if kind == 0x70:
            return None

        if kind == 0x09:
            self.read_u32()
            return None

        # full model reference
        model_id_kind = self.read_u8()

        # regular uuid
        if model_id_kind == 0x48:
            uuid = self.read_uuid()
            model_id = f"r:{uuid[0]:016x}{uuid[1]:016x}"
        elif model_id_kind == 0x70:
            model_id = ""
        else:
            raise RuntimeError(
                f"Unsupported model_id_kind 0x{model_id_kind:02X} at pos {self.pos}"
            )

        self.read_string()
        return model_id
