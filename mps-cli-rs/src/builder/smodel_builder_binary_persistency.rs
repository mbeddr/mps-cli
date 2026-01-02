use std::{cell::RefCell, collections::HashMap, io::Read, path::PathBuf, rc::Rc};

use crate::model::{slanguage::SLanguage, smodel::SModel};
use super::{slanguage_builder::SLanguageBuilder, smodel_builder_base::{SModelBuilderCache}};

pub(crate) fn build_model<'a>(mpb_file: PathBuf, language_id_to_slanguage: &'a mut HashMap<String, SLanguage>, language_builder : &mut SLanguageBuilder, model_builder_cache : &mut SModelBuilderCache) -> Rc<RefCell<SModel>> {
    let ext = mpb_file.extension();
    if !ext.is_some_and(|e| e.eq_ignore_ascii_case("mpb")) {
        panic!("expected file with extension .mpb but found '{}'", mpb_file.to_str().unwrap());        
    }

    let file = std::fs::File::open(mpb_file.clone());  
    if file.is_err() {
        panic!("file not found '{}'", mpb_file.to_str().unwrap());
    }

    println!("......... {}", mpb_file.to_str().unwrap());

    let name = "test".to_string();
    let uuid = "uuid".to_string();    
    let model: Rc<RefCell<SModel>> = model_builder_cache.get_model(name, uuid);
    
    model
}