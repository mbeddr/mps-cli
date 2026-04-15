import struct

from mpscli.model.builder.binary.constants import (
    NULL,
    STRING_INDEX,
    MODELREF_INDEX,
    MODELID_REGULAR,
    MODULEID_REGULAR,
    MODULEID_FOREIGN,
    MODULEREF_MODULEID,
    MODULEREF_NAMEONLY,
    MODULEREF_INDEX,
)
from mpscli.model.builder.binary.uuid_utils import uuid_str as _uuid_str


class ModelInputStream:

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        # The string table accumulates every new string seen during parsing..
        # Java's ModelInputStream maintains the same myStringss list.
        # Strings are appended on first encounter and referenced by index thereafter
        # The table is per-stream-instance so not really shared across files
        self.string_table: list = []

    def tell(self) -> int:
        # no direct Java equivalent, this is Python-specific helper to get the current stream position
        # for error messages and stream integrity checks
        return self.pos

    def seek(self, pos: int):
        # no direct Java equivalent: Python-specific helper used when we need to rewind one
        # byte (ex: the optional HEADER_ATTRIBUTES peek in V2 header parsing)
        # Java uses mark()/reset() on the underlying InputStream for the same purpose..
        self.pos = pos

    # this mirrors DataInputStream.readByte() - java.io.DataInputStream is the superclass of
    # jetbrains.mps.util.io.ModelInputStream and reads one unsignedd byte
    def read_u8(self) -> int:
        if self.pos >= len(self.data):
            raise RuntimeError(f"read_u8: EOF at pos {self.pos}")
        v = self.data[self.pos]
        self.pos += 1
        return v

    # mirrors DataInputStream.readBoolean() where it reads one byte, returns True if non-zero
    def read_bool(self) -> bool:
        return self.read_u8() != 0

    # mirrors DataInputStream.readShort(): reads 2 bytes big-endian as unsigned short
    # Java's readShort() returns a signed short. Python uses unsigned here because counts and indices in the
    # registry are always I guess non-negative..
    def read_u16(self) -> int:
        if self.pos + 2 > len(self.data):
            raise RuntimeError(f"read_u16: EOF at pos {self.pos}")
        v = struct.unpack_from(">H", self.data, self.pos)[0]
        self.pos += 2
        return v

    # mirrors DataInputStream.readShort() - reads 2 bytes big-endian as signed short
    # used for the props_count field in the header which MPS writes as a signed short
    def read_i16(self) -> int:
        if self.pos + 2 > len(self.data):
            raise RuntimeError(f"read_i16: EOF at pos {self.pos}")
        v = struct.unpack_from(">h", self.data, self.pos)[0]
        self.pos += 2
        return v

    # mirrors DataInputStream.readInt(): reads 4 bytes big-endian as unsigned int
    # Java's readInt() returns a signed int. Python uses unsigned here because section markers and import counts
    # are always treated as unsigned values.
    def read_u32(self) -> int:
        if self.pos + 4 > len(self.data):
            raise RuntimeError(f"read_u32: EOF at pos {self.pos}")
        v = struct.unpack_from(">I", self.data, self.pos)[0]
        self.pos += 4
        return v

    # mirrors DataInputStream.readInt(): reads 4 bytes big-endian as signed int
    # used where MPS explicitly writes a signed value, example: the import usedVersion field (which can be -1)
    # and the old model version compatibility field
    def read_i32(self) -> int:
        if self.pos + 4 > len(self.data):
            raise RuntimeError(f"read_i32: EOF at pos {self.pos}")
        v = struct.unpack_from(">i", self.data, self.pos)[0]
        self.pos += 4
        return v

    # mirrors DataInputStream.readLong() - reads 8 bytess big-endian
    # used unsigned rather than signed because u64 is almost always safe for bit manipulation and hex formatting
    # wherein a signed negative value would produce a minus sign in :016x formatting and silently corrupt uuid strings.
    def read_u64(self) -> int:
        if self.pos + 8 > len(self.data):
            raise RuntimeError(f"read_u64: EOF at pos {self.pos}")
        v = struct.unpack_from(">Q", self.data, self.pos)[0]
        self.pos += 8
        return v

    # no direct Java equivalent: Python-specific helper used by read_string() to read a fixed number of raw bytes
    # from the stream
    def read_bytes(self, length: int) -> bytes:
        if self.pos + length > len(self.data):
            raise RuntimeError(
                f"read_bytes({length}): EOF at pos {self.pos}, "
                f"only {len(self.data) - self.pos} bytes left"
            )
        v = self.data[self.pos : self.pos + length]
        self.pos += length
        return v

    # mirrors ModelInputStream.readUUID() in
    # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/kernel/source/jetbrains/mps/util/io/ModelInputStream.java
    #
    # Java's readLong() reads a signed 64-bit integerr but we use read_u64() (unsigned) instead and this is
    # intentional and correct for the following reason:
    #
    # uuid halves are opaque 64-bit bit strings so the sign interpretation is quite irrelevant
    # both u64 and i64 read exactly the same 8 bytes in the same big-endian order.
    # The difference only shows when the value is used and we use UUID halves exclusively
    # for bit manipulation and hex formatting (:016x in _uuid_str()).
    #
    # Using u64 is actually much safer than i64 in Python where if the sign bit is set, i64 produces a negative
    # integer, and formatting a negative integer with :016x produces a minus sign which would silently corrupt the
    # uuid string but u64 always produces a non-negative integer so ':016x' formatting is always unambiguouss and correct.
    def read_uuid(self) -> tuple:
        high = self.read_u64()
        low = self.read_u64()
        return (high, low)

    # mirrors ModelInputStream.readString() in:
    # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/kernel/source/jetbrains/mps/util/io/ModelInputStream.java
    #
    # Dispatch on the first (kind) byte:
    #  NULL (0x70) - return None
    #  STRING_INDEX (0x01) - back-reference: read u32 index, return string_table[index]
    #  anything else - new string: read u16 length + UTF-8 bytes then append to tablee

    # Difference from Java: Java uses DataInputStream.readUTF() which reads a u16 length and then modified UTF-8.
    # Python reads the same u16 length then standard UTF-8. These are compatible for all characters in
    # binary model persistency
    def read_string(self):
        c = self.read_u8()

        if c == NULL:
            return None

        if c == STRING_INDEX:
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

    # mirrors ModelInputStream.readModuleReference() in:
    # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/kernel/source/jetbrains/mps/util/io/ModelInputStream.java
    #
    # Dispatch on kind byte:
    #  NULL (0x70) - return None
    #  MODULEREF_NAMEONLY (0x18) - name-only ref: read one string (module name, no id)
    #  MODULEREF_INDEX (0x19) - indexed back-ref: read u32 index into module-ref cache
    #  MODULEREF_MODULEID (0x17) - full ref with ModuleId sub-record:
    #   sub 0x70 (NULL) - null ModuleId (name-only fallback)
    #   sub 0x48 (REGULAR) - UUID-based id: read two u64 values
    #   sub 0x47 (FOREIGN) - string-based id: read one string
    #   then read string (module name) in all sub-cases
    def read_module_ref(self):
        kind = self.read_u8()

        if kind == NULL:
            return None

        if kind == MODULEREF_NAMEONLY:
            return {"type": "name_only", "name": self.read_string()}

        if kind == MODULEREF_INDEX:
            return {"type": "indexed", "index": self.read_u32()}

        if kind == MODULEREF_MODULEID:
            sub = self.read_u8()
            if sub == NULL:
                module_id = None
            elif sub == MODULEID_REGULAR:
                module_id = self.read_uuid()
            elif sub == MODULEID_FOREIGN:
                module_id = self.read_string()
            else:
                raise RuntimeError(
                    f"Unknown module id sub-type 0x{sub:02X} at pos {self.pos}"
                )
            name = self.read_string()
            return {"type": "full", "id": module_id, "name": name}

        raise RuntimeError(f"Unknown module ref kind 0x{kind:02X} at pos {self.pos}")

    # mirrors ModelInputStream.readModelReference() in -
    # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/kernel/source/jetbrains/mps/util/io/ModelInputStream.java
    #
    # Dispatch on kind byte:
    #  NULL (0x70) - return None
    #  MODELREF_INDEX (0x09) - indexed back-ref: read u32, return None
    #  anything else - full model reference:
    #   read model id kind byte:
    #    MODELID_REGULAR (0x48) - UUID-based: read 2xu64 and format ass "r:..."
    #    NULL (0x70) - empty/null model id
    #   read and discard model name string
    #
    # Difference: Java maintains a myModelRefs cache for MODELREF_INDEX back-references.
    # Python does not cache - model ref identity is not needed in our one-shot CLI reads.
    def read_model_ref(self):
        kind = self.read_u8()

        if kind == NULL:
            return None

        if kind == MODELREF_INDEX:
            self.read_u32()
            return None

        # full model reference
        model_id_kind = self.read_u8()

        # regular uuid
        if model_id_kind == MODELID_REGULAR:
            uuid = self.read_uuid()
            model_id = _uuid_str(uuid[0], uuid[1])
        elif model_id_kind == NULL:
            model_id = ""
        else:
            raise RuntimeError(
                f"Unsupported model_id_kind 0x{model_id_kind:02X} at pos {self.pos}"
            )

        self.read_string()
        return model_id
