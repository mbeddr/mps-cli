use std::{cell::RefCell, collections::HashMap, io::Read, path::PathBuf, rc::Rc};

use crate::model::{slanguage::SLanguage, smodel::SModel};
use super::{slanguage_builder::SLanguageBuilder, smodel_builder_base::{do_extract_model_core_info, SModelBuilderCache}};

pub(crate) fn build_model<'a>(mps_file: PathBuf, language_id_to_slanguage: &'a mut HashMap<String, SLanguage>, language_builder : &mut SLanguageBuilder, model_builder_cache : &mut SModelBuilderCache) -> Rc<RefCell<SModel>> {
    let ext = mps_file.extension();
    if ext.unwrap().to_ascii_lowercase() != "mps" {
        panic!("expected file with extension .mps but found '{}'", mps_file.to_str().unwrap());        
    }

    let file = std::fs::File::open(mps_file.clone());  
    if file.is_err() {
        panic!("file not found '{}'", mps_file.to_str().unwrap());
    }
    let mut s = String::new();
    let _ = file.unwrap().read_to_string(&mut s);
    let parse_res = roxmltree::Document::parse(&s);
    let document = parse_res.unwrap();
    
    let model: Rc<RefCell<SModel>> = do_extract_model_core_info(document, model_builder_cache, mps_file.to_str().unwrap().to_string());
    


    model
}