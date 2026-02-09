# mpscli/model/builder/binary/reader.py

class BinaryReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.strings = []

    def read_u8(self):
        val = self.data[self.pos]
        self.pos += 1
        return val

    def read_u16(self):
        val = int.from_bytes(self.data[self.pos:self.pos + 2], "big")
        self.pos += 2
        return val

    def read_u32(self):
        val = int.from_bytes(self.data[self.pos:self.pos + 4], "big")
        self.pos += 4
        return val

    def read_u64(self):
        val = int.from_bytes(self.data[self.pos:self.pos + 8], "big")
        self.pos += 8
        return val

    def read_bytes(self, length: int) -> bytes:
        val = self.data[self.pos:self.pos + length]
        self.pos += length
        return val
