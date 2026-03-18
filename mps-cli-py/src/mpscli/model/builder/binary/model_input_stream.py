import struct


class ModelInputStream:
    """
    Python equivalent of jetbrains.mps.util.io.ModelInputStream,
    used by BinaryPersistence.

    String encoding (EXACT match to Java):
        read 1 byte c
        c == 0x70  → NULL  (return None)
        c == 0x01  → string table ref: read u32 index, return string_table[index]
        else       → inline: read u16 length, read bytes, decode UTF-8,
                     append to string_table, return string
    """

    # ── Stream version constants ────────────────────────────────────────────
    STREAM_ID_V1 = 0x00000300
    STREAM_ID_V2 = 0x00000400
    STREAM_ID_V3 = 0x00000500

    # ── Registry stub constants (from BinaryPersistence.java) ───────────────
    STUB_NONE = 0x12  # always written after flags; concept has no stub
    STUB_ID = 0x13  # always written after flags; next u64 is stub concept id

    # ── Marker constants ────────────────────────────────────────────────────
    HEADER_START = 0x91ABABA9
    HEADER_END = 0xABABABAB
    REGISTRY_START = 0x5A5A5A5A
    REGISTRY_END = 0xA5A5A5A5
    MODEL_START = 0xBABABABA
    HEADER_ATTRIBUTES = 0x7E
    DEPENDENCY_V1 = 0x01

    # ────────────────────────────────────────────────────────────────────────

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.string_table: list = []

    # ── Positioning ──────────────────────────────────────────────────────────

    def tell(self) -> int:
        return self.pos

    def seek(self, pos: int):
        self.pos = pos

    # ── Primitives ───────────────────────────────────────────────────────────

    def read_u8(self) -> int:
        if self.pos >= len(self.data):
            raise RuntimeError(f"read_u8: EOF at pos {self.pos}")
        v = self.data[self.pos]
        self.pos += 1
        return v

    def read_bool(self) -> bool:
        return self.read_u8() != 0

    def read_u16(self) -> int:
        if self.pos + 2 > len(self.data):
            raise RuntimeError(f"read_u16: EOF at pos {self.pos}")
        v = struct.unpack_from(">H", self.data, self.pos)[0]
        self.pos += 2
        return v

    def read_i16(self) -> int:
        """Signed short — same as Java readShort()."""
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
        """Signed int — same as Java readInt()."""
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

    # ── UUID (two big-endian longs, as Java writeUUID/readUUID) ─────────────

    def read_uuid(self) -> tuple:
        high = self.read_u64()
        low = self.read_u64()
        return (high, low)

    # ── String (CRITICAL — exact match to Java ModelInputStream) ────────────

    def read_string(self):
        """
        Exact translation of ModelInputStream.readString():

            byte c = readByte();
            if (c == NULL)       return null;              // 0x70
            if (c == STRING_REF) return table[readInt()];  // 0x01
            // else: inline new string
            int len = readShort();   // unsigned 16-bit length
            byte[] buf = new byte[len];
            readFully(buf);
            String s = new String(buf, UTF_8);
            table.add(s);
            return s;
        """
        c = self.read_u8()

        if c == 0x70:  # NULL
            return None

        if c == 0x01:  # string table reference
            index = self.read_u32()
            if index >= len(self.string_table):
                raise RuntimeError(
                    f"String table index {index} out of range "
                    f"(table size={len(self.string_table)}) at pos {self.pos}"
                )
            return self.string_table[index]

        # Inline string: c is the discriminator byte (its value beyond not
        # being 0x70 or 0x01 does not matter). Read a fresh u16 for byte count.
        length = self.read_u16()
        raw = self.read_bytes(length)
        s = raw.decode("utf-8")
        self.string_table.append(s)
        return s

    # ── Module reference ─────────────────────────────────────────────────────

    def read_module_ref(self):
        """
        Reads a SModuleReference.

        kind byte:
            0x70  → NULL
            0x18  → name-only  → read_string()
            0x19  → indexed    → read_u32()
            0x17  → full id:
                        sub 0x70 → null id
                        sub 0x48 → uuid (2×u64)
                        sub 0x47 → string id
                    then read_string() for name
        """
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

    # ── Model reference ──────────────────────────────────────────────────────

    def read_model_ref(self):
        """
        Reads a SModelReference (used in imports).
        Returns a best-effort string model_id, or None.
        """
        kind = self.read_u8()

        if kind == 0x70:  # NULL
            return None

        if kind == 0x09:  # MODELREF_INDEX
            self.read_u32()
            return None

        # Full model reference
        model_id_kind = self.read_u8()

        if model_id_kind == 0x48:  # regular uuid
            uuid = self.read_uuid()
            model_id = f"r:{uuid[0]:016x}{uuid[1]:016x}"
        elif model_id_kind == 0x70:  # NULL id
            model_id = ""
        else:
            raise RuntimeError(
                f"Unsupported model_id_kind 0x{model_id_kind:02X} at pos {self.pos}"
            )

        self.read_string()  # model name — consumed
        return model_id
