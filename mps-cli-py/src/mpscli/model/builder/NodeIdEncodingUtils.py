class NodeIdEncodingUtils:
    INDEX_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz$_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    MIN_CHAR = ord("$")

    def __init__(self):
        self._char_to_value = {}
        for i, ch in enumerate(self.INDEX_CHARS):
            self._char_to_value[ord(ch) - self.MIN_CHAR] = i

    def decode(self, uid_string: str) -> str:
        if not uid_string:
            return ""

        res = self._char_to_value[ord(uid_string[0]) - self.MIN_CHAR]

        for ch in uid_string[1:]:
            res = res << 6
            res |= self.INDEX_CHARS.index(ch)

        return str(res)

    def encode(self, decimal_string: str) -> str:
        try:
            uid_number = int(decimal_string)
        except ValueError:
            return "Invalid decimal input"

        if uid_number == 0:
            return self.INDEX_CHARS[0]

        result = []

        while uid_number > 0:
            remainder = uid_number % 64
            result.append(self.INDEX_CHARS[remainder])
            uid_number //= 64

        result.reverse()
        return "".join(result)
