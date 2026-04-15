# mpscli/model/builder/binary/constants.py
#
# The following constants are taken from:
# https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BinaryPersistence.java
#
# Section boundary markers where each is a fixed 4-byte number(i32) written at the start or end of a major
# section in the .mpb stream. The reader asserts the expected valuee at each point and if there is a
# mismatch means the stream is corrupt or the reader is misaligned.
HEADER_START = 0x91ABABA9
HEADER_END = 0xABABABAB
REGISTRY_START = 0x5A5A5A5A
REGISTRY_END = 0xA5A5A5A5
MODEL_START = 0xBABABABA
# stream version identifiers which are written as the second i32 in the header..
# In MPS 2024.1, STREAM_ID = STREAM_ID_V2 (0x400) where V2 is the only active format.
# V3 format was introduced later and added the module-ref in header, persistedCapabilities byte, DEPENDENCY_V1 byte,
# and per-language import versions.
# Our Python implementation reads both V2 and V3 defensively for forward compatibility.
# V1 format is is rejected and the MPS itself refuses to read it as well
STREAM_ID_V1 = 0x00000300
STREAM_ID_V2 = 0x00000400
STREAM_ID_V3 = 0x00000500
STREAM_ID = STREAM_ID_V2
HEADER_ATTRIBUTES = 0x7E
STUB_NONE = 0x12
STUB_ID = 0x13
DEPENDENCY_V1 = 0x01


# The following constants are taken from
# https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/kernel/source/jetbrains/mps/util/io/ModelOutputStream.java

# universal null marker
NULL = 0x70
STRING_INDEX = 0x01
STRING_INLINE = 0x02
NODEID_LONG = 0x18
NODEID_STRING = 0x17
NODE_OPEN_BRACE = 0x7B
NODE_CLOSE_BRACE = 0x7D
AGG_INDEX_NONE = 0xFFFF
MODELREF_INDEX = 0x09
MODELID_REGULAR = 0x28
MODELID_FOREIGN = 0x26
MODULEID_REGULAR = 0x48
MODULEID_FOREIGN = 0x47
MODULEREF_MODULEID = 0x17
MODULEREF_NAMEONLY = 0x18
MODULEREF_INDEX = 0x19


# The following constants are taken from
# https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BareNodeWriter.java
REF_THIS_MODEL = 0x11
REF_OTHER_MODEL = 0x12
