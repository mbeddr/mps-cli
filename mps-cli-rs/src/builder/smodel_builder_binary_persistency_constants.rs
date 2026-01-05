
// the following constants are taken from 
// https://github.com/JetBrains/MPS/blob/f9075b2832077358fd85a15a52bba76a9dad07a3/core/persistence/source/jetbrains/mps/persistence/binary/BinaryPersistence.java
pub const HEADER_START : u32 = 0x91ABABA9;
pub const HEADER_END : u32   = 0xabababab;
pub const STREAM_ID_V2 : u32 = 0x00000400;
pub const STREAM_ID : u32   = STREAM_ID_V2;

pub const REGISTRY_START : u32 = 0x5a5a5a5a;
pub const REGISTRY_END : u32   = 0xa5a5a5a5;

// the following constants are taken from 
// https://github.com/JetBrains/MPS/blob/f9075b2832077358fd85a15a52bba76a9dad07a3/core/kernel/source/jetbrains/mps/util/io/ModelOutputStream.java
pub const NULL: u8 = 0x70;
pub const MODELREF_INDEX: u8 = 9;

pub const MODELID_REGULAR: u8 = 0x28;
