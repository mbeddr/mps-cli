
class NodeIdEncodingUtils:
    
    def __init__(self):
        self.myIndexChars = "0123456789abcdefghijklmnopqrstuvwxyz$_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.MIN_CHAR = ord('$')
        self.myCharToValue = {}
        for i in range(0, len(self.myIndexChars)):
            charValue = ord(self.myIndexChars[i])
            self.myCharToValue[charValue - self.MIN_CHAR] = i

    # transforms the node id string saved in MPS files and converts it to the proper node id as long 
    def decode_string(self, uid_string):
        res = 0
        c = uid_string[0]
        value = self.myCharToValue[ord(c) - self.MIN_CHAR]
        res = value
        for idx in range(1, len(uid_string)):
            res = res << 6
            c = uid_string[idx]
            value = self.myIndexChars.index(c)
            res = res | value
        return res
      