use std::io::{Cursor, Read};
use byteorder::{BigEndian, ReadBytesExt};
use uuid::Uuid;
use crate::builder::smodel_builder_binary_persistency_constants::*;
 

pub(crate) fn read_uuid(cursor: &mut Cursor<&Vec<u8>>) -> String {
    let head_bits = cursor.read_u64::<BigEndian>().expect("failed to read u64 head_bits");
    let tail_bits = cursor.read_u64::<BigEndian>().expect("failed to read u64 tail_bits");
    return Uuid::from_u64_pair(head_bits, tail_bits).as_hyphenated().to_string();
}

pub(crate) fn read_string(cursor: &mut Cursor<&Vec<u8>>, my_strings: &mut Vec<String>) -> String {
    let c = cursor.read_u8().expect("failed to read u8");
    if c == NULL {
      return "".to_string();
    } else if c == 1 {
      let index = cursor.read_u32::<BigEndian>().expect("failed to read u32") as usize;
      return my_strings[index].clone();
    }

    let string_size = cursor.read_u16::<BigEndian>().expect("failed to read u32") as usize;
    println!(".........reading string of size: {}", string_size);

    let mut sb = String::new();
    let mut buf = vec![0u8; string_size];
    cursor.read_exact(&mut buf).expect("failed to read string bytes");
    sb.push_str(&String::from_utf8_lossy(&buf));
    my_strings.push(sb.clone());

    println!(".........reading string: {}", sb);
    return sb;
  }

  pub(crate) fn advance_cursor_until_after(cursor: &mut Cursor<&Vec<u8>>, marker: u32) {
    let mut current_pos = cursor.position();
    let end_pos = cursor.get_ref().len() as u64;

    while current_pos < end_pos {
      let byte = cursor.read_u8().expect("failed to read u8");
      // Read 4 bytes and compare to marker (u32)
      if current_pos + 4 <= end_pos {
        let mut buf = [0u8; 4];
        buf[0] = byte;
        cursor.read_exact(&mut buf[1..]).expect("failed to read marker bytes");
        let found = u32::from_be_bytes(buf);
        if found == marker {
          return;
        } else {
          // Move back 3 bytes to check next possible 4-byte window
          cursor.set_position(cursor.position() - 3);
          current_pos = cursor.position();
        }
      } else {
        break;
      }
      current_pos += 1;
    }
  }