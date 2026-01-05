use std::{cell::RefCell, collections::HashMap, io::Read, path::PathBuf, rc::Rc};

use crate::model::{slanguage::SLanguage, smodel::SModel};
use super::{slanguage_builder::SLanguageBuilder, smodel_builder_base::{SModelBuilderCache}};
use std::io::Cursor;
use byteorder::{BigEndian, ReadBytesExt, WriteBytesExt};
use crate::builder::smodel_builder_binary_persistency_constants::*;
use crate::builder::smodel_builder_binary_persistency_utils::*;

pub(crate) fn build_model<'a>(mpb_file: PathBuf, 
                              language_id_to_slanguage: &'a mut HashMap<String, SLanguage>, 
                              language_builder : &mut SLanguageBuilder, 
                              model_builder_cache : &mut SModelBuilderCache) -> Rc<RefCell<SModel>> {
    let ext = mpb_file.extension();
    if !ext.is_some_and(|e| e.eq_ignore_ascii_case("mpb")) {
        panic!("expected file with extension .mpb but found '{}'", mpb_file.to_str().unwrap());        
    }

    println!(".........reading file: {}", mpb_file.to_str().unwrap());

    let file = std::fs::File::open(mpb_file.clone());  
    if file.is_err() {
        panic!("error while opening the file '{}'", mpb_file.to_str().unwrap());
    }

    let mut buffer = Vec::new();
    file.unwrap().read_to_end(&mut buffer).expect("failed to read file as binary");

    let mut cursor: Cursor<&Vec<u8>> = Cursor::new(&buffer);
    
    let mut my_model_refs= Vec::<Rc<RefCell<SModel>>>::new();
    let mut my_strings= Vec::<String>::new();
    
    let mut crt_model : Rc<RefCell<SModel>> = read_model_header(&mut cursor, &mpb_file, &mut my_model_refs, &mut my_strings, model_builder_cache);

    load_model_properties(&mut cursor, &mpb_file, model_builder_cache);

    return crt_model;
}

// BinaryPersistency::loadModelProperties
pub(crate) fn load_model_properties(cursor: &mut Cursor<&Vec<u8>>, 
                                     mpb_file: &PathBuf, 
                                     model_builder_cache: &mut SModelBuilderCache) {
    
}

pub(crate) fn read_model_header(cursor: &mut Cursor<&Vec<u8>>, 
                                mpb_file: &PathBuf, 
                                my_model_refs: &mut Vec<Rc<RefCell<SModel>>>, 
                                my_strings: &mut Vec<String>, 
                                model_builder_cache: &mut SModelBuilderCache) -> Rc<RefCell<SModel>> {

    let crt_model : Rc<RefCell<SModel>>;
    let header = cursor.read_u32::<BigEndian>().expect("failed to read u32 header");
    if !(header == HEADER_START) {
        panic!("unexpected header: 0x{:X} in file {}", header, mpb_file.to_str().unwrap());
    }
    let stream_id = cursor.read_u32::<BigEndian>().expect("failed to read u32 streamId");
    if stream_id != STREAM_ID {
        panic!("unexpected stream ID: 0x{:X} in file {}", stream_id, mpb_file.to_str().unwrap());
    }

    let crt_byte= cursor.read_u8().expect("failed to read u8 crtByte");
    if crt_byte == NULL {
        panic!("unexpected byte NULL but model_ref in file {}", mpb_file.to_str().unwrap());
    } else if crt_byte == MODELREF_INDEX {
      let index = cursor.read_u32::<BigEndian>().expect("failed to read u32 modelRefIndex") as usize;
      crt_model = my_model_refs[index].clone();
    } else {
      let model_id = read_model_id(cursor);
      let model_name = read_string(cursor, my_strings);
      crt_model = model_builder_cache.get_model(model_name, model_id);    

      advance_cursor_until_after(cursor, HEADER_END);

      let c = cursor.read_u8().expect("failed to read u8");
      
      my_model_refs.push(crt_model.clone());
    }

    return crt_model;
}
 
pub(crate) fn read_model_id(cursor: &mut Cursor<&Vec<u8>>) -> String {
    let c = cursor.read_u8().expect("failed to read u8");
    if (c == NULL) {
      return "".to_string();
    } else if (c == MODELID_REGULAR) {
      return read_uuid(cursor);
    } else {
      panic!("unknown id format 0x{:X}", c);
    }
}
#[cfg(test)]
mod tests {
  use super::*;

  #[test]
  fn test_read_model_header_regular_model() {
    let model_name = "TestModel";
    let model_id = "12345678-1234-5678-1234-567812345678";

    let mut buf = Vec::new();
    // HEADER_START
    buf.write_u32::<BigEndian>(HEADER_START).unwrap();
    // STREAM_ID
    buf.write_u32::<BigEndian>(STREAM_ID).unwrap();
    // Not NULL, not MODELREF_INDEX, so use MODELID_REGULAR
    buf.write_u8(MODELID_REGULAR).unwrap();
    // Write UUID (simulate)
    let uuid_bytes = model_id.as_bytes( );
    buf.extend_from_slice(uuid_bytes);
    // Write model name as string (simulate)
    let name_bytes = model_name.as_bytes();
    buf.write_u32::<BigEndian>(name_bytes.len() as u32).unwrap();
    buf.extend_from_slice(name_bytes);
    // HEADER_END
    buf.write_u32::<BigEndian>(HEADER_END).unwrap();
    // Next byte after model
    buf.write_u8(0xAA).unwrap();

    let mut cursor = Cursor::new(&buf);
    let mpb_file = PathBuf::from("test.mpb");
    let mut my_model_refs = Vec::<Rc<RefCell<SModel>>>::new();
    let mut my_strings = Vec::<String>::new();
    let mut cache = SModelBuilderCache::new();

    let model_rc = read_model_header(&mut cursor, &mpb_file, &mut my_model_refs, &mut my_strings, &mut cache);

    let model = model_rc.borrow();
    assert_eq!(model.name, model_name);
    assert_eq!(model.uuid, model_id);
  }

  #[test]
  #[should_panic(expected = "unexpected header: 0xDEADBEEF in file test.mpb")]
  fn test_read_model_header_invalid_header() {
    let mut buf = Vec::new();
    buf.write_u32::<BigEndian>(0xDEADBEEF).unwrap(); // Invalid header
    buf.write_u32::<BigEndian>(STREAM_ID).unwrap();
    buf.write_u8(MODELID_REGULAR).unwrap();
    let mut cursor = Cursor::new(&buf);

    let mpb_file = PathBuf::from("test.mpb");
    let mut my_model_refs = Vec::<Rc<RefCell<SModel>>>::new();
    let mut my_strings = Vec::<String>::new();
    let mut cache = SModelBuilderCache::new();

    let _ = read_model_header(&mut cursor, &mpb_file, &mut my_model_refs, &mut my_strings, &mut cache);
  }
}
