use std::{cell::RefCell, collections::HashMap, io::Read, path::PathBuf, rc::Rc};

use crate::model::sconcept::{SConcept, SContainmentLink, SProperty, SReferenceLink};
use crate::model::{slanguage::SLanguage, smodel::SModel};
use crate::model::snode::SNode;
use super::{slanguage_builder::SLanguageBuilder, smodel_builder_base::{SModelBuilderCache}};
use std::io::Cursor;
use byteorder::{BigEndian, ReadBytesExt};
use crate::builder::smodel_builder_binary_persistency_constants::*;
use crate::builder::smodel_builder_binary_persistency_utils::*;
use super::slanguage_builder::{get_or_build_language};

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

    load_model_properties(&mut cursor, &mpb_file, model_builder_cache, language_builder, language_id_to_slanguage, crt_model.clone(), &mut my_strings);

    advance_cursor_until_after(&mut cursor, MODEL_START);
    read_children(&mut cursor, model_builder_cache, &mut my_strings, crt_model.clone());

    return crt_model;
}


pub(crate) fn read_children(cursor: &mut Cursor<&Vec<u8>>, model_builder_cache : &mut SModelBuilderCache, my_strings: &mut Vec<String>, model : Rc<RefCell<SModel>>) {
    let child_count : u32 = cursor.read_u32::<BigEndian>().expect("failed to read u32 child count");
    println!("...child count: {}", child_count);
    for _ in 0..child_count {
        let rootNode: Rc<SNode> = read_node(cursor, None, model_builder_cache, my_strings, model.clone());
        model.borrow_mut().root_nodes.push(rootNode);
    }
}

pub(crate) fn read_node(cursor: &mut Cursor<&Vec<u8>>, parent : Option<&mut SNode>, model_builder_cache : &mut SModelBuilderCache, my_strings: &mut Vec<String>, model : Rc<RefCell<SModel>>) -> Rc<SNode> {
    let concept_index: u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 concept index");
    let concept: &Rc<SConcept> = model_builder_cache.index_2_concept.get(&concept_index.to_string()).expect("concept not found by index");

    let mut nodeid: String = read_node_id(cursor, my_strings);

    let mut node= SNode::new(nodeid.clone(), concept.clone(), None);
    println!("...node: {} - {}", nodeid, concept.name);

    let aggregation_index : u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 aggregation index");

    let open_curly: char = cursor.read_u8().expect("failed to read u8") as char;
    if open_curly != '{' {
        panic!("bad stream, no '{{'");
    }

    let properties_count : u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 properties count");
    println!("...properties count: {}", properties_count);
    for _ in 0..properties_count {
        let property_index: u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16");
        let property: &Rc<SProperty> = model_builder_cache.index_2_property.get(&property_index.to_string()).expect("property not found by index");
        let property_value = read_string(cursor, my_strings);
        println!("......property: {} - {}", property.name, property_value);
        node.add_property(property, property_value);
    }
    
    let user_objects_count : u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 user-objects count");
    if user_objects_count !=0 {
      panic!("user-objects are not supported yet");
    }

    let references_count : u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 references count");
    println!("...references count: {}", references_count);
    for _ in 0..references_count {
        let reference_index: u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16");
        let reference: &Rc<SReferenceLink> = model_builder_cache.index_2_reference_link.get(&reference_index.to_string()).expect("reference not found by index");
        
        let kind : u8 = cursor.read_u8().expect("failed to read u8");
        if kind != 1 && kind != 2 && kind != 3 {
            panic!("unknown reference kind: {}", kind);
        }
        if kind == 1 {
          let reference_nodeid = read_node_id(cursor, my_strings);
          let mut target_model_kind: u8 = cursor.read_u8().expect("failed to read u8");
          if (target_model_kind != REF_OTHER_MODEL && target_model_kind != REF_THIS_MODEL) {
              panic!("unknown target model kind: {}", target_model_kind);
          }
          let mut model_ref_id : String;
          if (target_model_kind == REF_OTHER_MODEL) {
            model_ref_id = read_model_reference(cursor, model_builder_cache);
          } else { // THIS_MODEL
            model_ref_id = model.borrow().uuid.clone();
          } 

          let resolve_info = read_string(cursor, my_strings);
          node.add_reference(reference, model_ref_id.clone(), reference_nodeid.clone(), Some(resolve_info.clone()));
          println!("......reference: {} - {}@{} - resolveInfo: {}", reference.name, model_ref_id, reference_nodeid, resolve_info);
        } else {
          panic!("reference kinds 2 and 3 are not supported yet");
        }
    }

    let node_rc = Rc::new(node);
    if let Some(parent) = parent {
        let link: &Rc<SContainmentLink> = model_builder_cache.index_2_containment_link.get(&aggregation_index.to_string()).expect("link not found by index");
        parent.add_child(link.clone(), node_rc.clone());
    }

    read_children(cursor, model_builder_cache, my_strings, model);

    let closed_curly: char = cursor.read_u8().expect("failed to read u8") as char;
    if closed_curly != '}' {
        panic!("bad stream, no '}}'");
    }

    return node_rc;
}

// ToDo: we currently only SKIP over module references
pub(crate) fn read_module_reference(cursor: &mut Cursor<&Vec<u8>>, my_strings: &mut Vec<String>) {
    let c = cursor.read_u8().expect("failed to read u8");
    if c == MODULEREF_INDEX {
      cursor.read_u32::<BigEndian>().expect("failed to read u32");
      // we do nothing with this information
    } else if c == MODULEREF_MODULEID {
      let c = cursor.read_u8().expect("failed to read u8");
      if c == NULL {
        // do nothing
      } else if c == MODULEID_REGULAR {
        read_uuid(cursor);
      } else if c == MODULEID_FOREIGN {
        read_string(cursor, my_strings);
      }
    } else {
      panic!("unknown model reference format 0x{:X}", c);
    }
}

pub(crate) fn read_model_reference(cursor: &mut Cursor<&Vec<u8>>, model_builder_cache : &SModelBuilderCache) -> String {
    let c = cursor.read_u8().expect("failed to read u8");
    if c == MODELREF_INDEX {
      let model_index: u32 = cursor.read_u32::<BigEndian>().expect("failed to read u32");
      return model_builder_cache.index_2_imported_model_uuid.get(&model_index.to_string()).expect("model id not found by index").to_string();
    } else {
      panic!("unexpected model reference format 0x{:X}", c);
    }
}

pub(crate) fn read_and_add_model_reference(cursor: &mut Cursor<&Vec<u8>>, model_builder_cache : &mut SModelBuilderCache, my_strings: &mut Vec<String>, index : String) -> String {
  let c = cursor.read_u8().expect("failed to read u8");
  if c == MODELREF_INDEX {
    panic!("unexpected MODELREF_INDEX when reading and adding model reference");
  }  
  
  let model_id = read_model_id(cursor);
  let _model_name = read_string(cursor, my_strings);
  read_module_reference(cursor, my_strings);
  model_builder_cache.index_2_imported_model_uuid.insert(index, model_id.clone());
  return model_id;
}

pub(crate) fn read_node_id(cursor: &mut Cursor<&Vec<u8>>, my_strings: &mut Vec<String>) -> String {
    let mut nodeid: String = "".to_string();
    let c : u8 = cursor.read_u8().expect("failed to read u8");
    if c == NODEID_LONG {
      let long_id: u64 = cursor.read_u64::<BigEndian>().expect("failed to read u64");
      nodeid = format!("{}", long_id);
    } else if c == NODEID_STRING {
      nodeid = read_string(cursor, my_strings);
    }
    return nodeid;
}

// BinaryPersistency::loadModelProperties
pub(crate) fn load_model_properties(cursor: &mut Cursor<&Vec<u8>>, 
                                     mpb_file: &PathBuf, 
                                     model_builder_cache: &mut SModelBuilderCache,
                                     language_builder : &mut SLanguageBuilder,
                                     language_id_to_slanguage: &mut HashMap<String, SLanguage>,
                                     model : Rc<RefCell<SModel>>,
                                     my_strings: &mut Vec<String>) {
    advance_cursor_until_after(cursor, REGISTRY_START);
    load_registry(cursor, model_builder_cache, my_strings,language_builder, language_id_to_slanguage);
    advance_cursor_until_after(cursor, REGISTRY_END);

    //BinaryPersistence::loadUsedLanguages
    let used_languages_count = cursor.read_u16::<BigEndian>().expect("failed to read u16 used languages count");
    println!("...languages count: {}", used_languages_count);
    for _ in 0..used_languages_count {
        let lang_id = read_uuid(cursor);
        let lang_name = read_string(cursor, my_strings);
        // we do nothing with this information
    }

    //BinaryPersistence::loadModuleRefList
    let modules_ref_count : u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 modules ref count");
    println!("...modules ref count: {}", modules_ref_count);
    for _ in 0..modules_ref_count {
        read_module_reference(cursor, my_strings)
    }

    //BinaryPersistence::loadImports
    let imports_count : u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 imports count");
    println!("...imports count: {}", imports_count);
    for import_index in 0..imports_count {
        read_and_add_model_reference(cursor, model_builder_cache, my_strings, import_index.to_string());
    }

}

pub(crate) fn load_registry(cursor: &mut Cursor<&Vec<u8>>, 
                             model_builder_cache: &mut SModelBuilderCache,
                             my_strings: &mut Vec<String>,
                             language_builder : &mut SLanguageBuilder,
                             language_id_to_slanguage: &mut HashMap<String, SLanguage>) {
    let lan_count : u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 language count");
    println!("...language count: {}", lan_count);
    let mut concept_index: u32 = 0;
    let mut property_index: u32 = 0;
    let mut reference_link_index: u32 = 0;
    let mut aggregation_link_index: u32 = 0;
    for _ in 0..lan_count {
        let lan_id = read_uuid(cursor);
        let lan_name = read_string(cursor, my_strings);

        let lang = get_or_build_language(&lan_id.to_string(), &lan_name.to_string(), language_id_to_slanguage);
        println!("...language: {} - {}", lan_id, lan_name);

        let concept_count : u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 concept count");
        println!("...concept count: {}", concept_count);
        for _ in 0..concept_count {
            let concept_id = cursor.read_u64::<BigEndian>().expect("failed to read u64 concept id");
            let concept_name = read_string(cursor, my_strings);

            // not used
            let flags = cursor.read_u8().expect("failed to read u8 flags");
            let stub_token = cursor.read_u8().expect("failed to read u8 stubToken");
            print!("...concept flags: 0x{:X}, stubToken: 0x{:X}", flags, stub_token);

            let conc = language_builder.get_or_create_concept(lang, concept_id.to_string().as_str(), concept_name.as_str());
            model_builder_cache.index_2_concept.insert(concept_index.to_string(), Rc::clone(&conc));
            concept_index += 1;
            println!("......concept: {} - {}", conc.name, concept_name);

            let property_count : u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 property count");
            println!("...property count: {}", property_count);
            for _ in 0..property_count {
                let prop_id = cursor.read_u64::<BigEndian>().expect("failed to read u64 property id");
                let prop_name = read_string(cursor, my_strings);
                let _prop = language_builder.get_or_create_property(Rc::clone(&conc), prop_id.to_string(), prop_name);
                model_builder_cache.index_2_property.insert(property_index.to_string(), Rc::clone(&_prop));
                property_index += 1;
                println!("......property: {} - {}", prop_id, _prop.name);
            }

            let association_count : u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 association count");
            println!("...association count: {}", association_count);
            for _ in 0..association_count {
                let link_id = cursor.read_u64::<BigEndian>().expect("failed to read u64 link id");
                let link_name = read_string(cursor, my_strings);
                let _link = language_builder.get_or_create_reference(Rc::clone(&conc), link_id.to_string(), link_name);
                model_builder_cache.index_2_reference_link.insert(reference_link_index.to_string(), Rc::clone(&_link));
                reference_link_index += 1;
                println!("......property: {} - {}", link_id, _link.name);

            }

            let aggregation_count : u16 = cursor.read_u16::<BigEndian>().expect("failed to read u16 aggregation count");
            println!("...aggregation count: {}", aggregation_count);
            for _ in 0..aggregation_count {
                let link_id = cursor.read_u64::<BigEndian>().expect("failed to read u64 link id");
                let link_name = read_string(cursor, my_strings);
                let unordered = cursor.read_u8().expect("failed to read u8 unordered") != 0;
                let _link = language_builder.get_or_create_child(Rc::clone(&conc), link_id.to_string(), link_name);
                model_builder_cache.index_2_containment_link.insert(aggregation_link_index.to_string(), Rc::clone(&_link));
                aggregation_link_index += 1;
                println!("......aggregation link: {} - {}", link_id, _link.name);
            }
        }
    }
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
  use byteorder::WriteBytesExt;

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
