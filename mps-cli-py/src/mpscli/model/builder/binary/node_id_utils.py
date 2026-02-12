class NodeIdEncodingUtils:
    INDEX_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz$_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    MIN_CHAR = ord("$")

    def __init__(self):
        self.char_to_value = {}
        for i, ch in enumerate(self.INDEX_CHARS):
            key = ord(ch) - self.MIN_CHAR
            self.char_to_value[key] = i

    def encode(self, uid_string: str) -> str:
        try:
            num = int(uid_string)
        except ValueError:
            return uid_string

        if num == 0:
            return self.INDEX_CHARS[0]

        result = []

        while num > 0:
            pos = num % 64
            result.append(self.INDEX_CHARS[pos])
            num //= 64

        result.reverse()
        return "".join(result)

    def decode(self, uid_string: str) -> str:
        if not uid_string:
            return ""

        res = 0

        for ch in uid_string:
            res = res << 6
            value = self.INDEX_CHARS.find(ch)
            if value == -1:
                raise ValueError(f"Invalid encoded node id character: {ch}")
            res |= value

        return str(res)
