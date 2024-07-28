use std::collections::HashMap;
use std::path::PathBuf;
use std::io::Read;
use roxmltree::Document;
use std::rc::Rc;
use std::cell::RefCell;

use walkdir::{DirEntry, WalkDir};

use crate::model::slanguage::SLanguage;
use crate::model::smodel::SModel;
use crate::model::snode::SNode;
use super::slanguage_builder::SLanguageBuilder;
use super::smodel_builder_base::{do_build_root_nodes, do_extract_model_core_info};
use super::smodel_builder_base::SModelBuilderCache;


pub(crate) fn build_model<'a>(path_to_model: PathBuf, language_id_to_slanguage: &'a mut HashMap<String, SLanguage>, language_builder : &mut SLanguageBuilder, model_builder_cache : &mut SModelBuilderCache) -> Rc<RefCell<SModel>> {
    let mut model_file = path_to_model.clone();
    model_file.push(".model");
    let model: Rc<RefCell<SModel>> = extract_model_core_info(model_file, model_builder_cache);
    
    let mpsr_file_walker = WalkDir::new(path_to_model).min_depth(1).max_depth(1);
    let mpsr_files = mpsr_file_walker.into_iter().filter(|entry| {
        if entry.is_ok() {
            let dir_entry = entry.as_ref().unwrap();
            let extension = dir_entry.path().extension();
            return dir_entry.file_type().is_file() && extension.is_some_and(|e| e.eq_ignore_ascii_case("mpsr"));
        }
        return false;
    });

    let mut roots = vec!();
    for mpsr_file in mpsr_files.into_iter() {
        let file = mpsr_file.unwrap();
        let r= build_root_node_from_file(file, language_id_to_slanguage, language_builder, model_builder_cache, &model);
        roots.extend(r);
    };
    model.as_ref().borrow_mut().root_nodes.extend(roots);

    return model;
}

fn extract_model_core_info<'a>(path_to_model: PathBuf, model_builder_cache : &mut SModelBuilderCache) -> Rc<RefCell<SModel>> {
    let path_to_model_file = path_to_model.to_str().unwrap().to_string();        

    let file = std::fs::File::open(path_to_model_file.clone());  
    if file.is_err() {
        panic!("file not found '{}'", path_to_model_file);
    }
    let mut s = String::new();
    let _ = file.unwrap().read_to_string(&mut s);
    let parse_res = Document::parse(&s);
    let document = parse_res.unwrap();

    do_extract_model_core_info(&document, model_builder_cache, path_to_model_file)
}


fn build_root_node_from_file<'a>(dir_entry: DirEntry, language_id_to_slanguage: &'a mut HashMap<String, SLanguage>, language_builder : &mut SLanguageBuilder, model_builder_cache : &mut SModelBuilderCache, crt_model : &Rc<RefCell<SModel>>) -> Vec<Rc<SNode>> {        
    let file = std::fs::File::open(dir_entry.path().as_os_str());  

    let mut s = String::new();
    let _ = file.unwrap().read_to_string(&mut s);
    let parse_res = roxmltree::Document::parse(&s);
          
    let document = parse_res.unwrap();
    do_build_root_nodes(&document, model_builder_cache, language_id_to_slanguage, language_builder, crt_model)    
}


#[cfg(test)]
mod tests {
    use std::path::PathBuf;

    use crate::builder::smodel_builder_file_per_root_persistency::{SModelBuilderCache, extract_model_core_info};

    #[test]
    fn test_model_extract_core_info() {
        // given
        let path = "../mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.library_top/.model"; 
        let path_to_model_file = PathBuf::from(path);

        //when
        let mut model_builder_cache = SModelBuilderCache::new();
        let temp = extract_model_core_info(path_to_model_file, &mut model_builder_cache);
        let model = temp.borrow();

        //assert
        assert_eq!(model.name, "mps.cli.lanuse.library_top.library_top");
        assert_eq!(model.uuid, "r:a96b23f6-56db-490c-a218-d40d11be7f1e");
        assert_eq!(model.path_to_model_file, path);
        assert_eq!(model.is_do_not_generate, true);
        assert!(model.is_file_per_root_persistency);
        assert_eq!(model.imported_models.len(), 1);
        let import = model.imported_models.first().unwrap();
        assert_eq!(import.borrow_mut().name, "mps.cli.lanuse.library_top.authors_top");
        assert_eq!(import.borrow_mut().uuid, "r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed");
    }

}
