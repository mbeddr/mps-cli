use std::cell::RefCell;
use std::path::PathBuf;
use std::time::Instant;

use std::io::Read;
use walkdir::WalkDir;

use crate::builder::smodel_builder_file_per_root_persistency::SModelBuilderFilePerRootPersistency;
use crate::builder::slanguage_builder::SLanguageBuilder;
use crate::model::ssolution::SSolution;

use super::smodel_builder_file_per_root_persistency::SModelBuilderCache;

pub(crate) fn build_solution<'a>(path_buf_to_msd_file: &PathBuf, language_builder : &mut SLanguageBuilder, model_builder_cache : &RefCell<SModelBuilderCache>) -> SSolution {
    let now = Instant::now();
    
    let path_to_msd_file = path_buf_to_msd_file.to_str().unwrap().to_string();
    let mut solution: SSolution = extract_solution_core_info(path_to_msd_file);
    let solution_dir = path_buf_to_msd_file.parent().unwrap();
    let model_dir = solution_dir.to_path_buf().to_str().unwrap().to_string() + "/models";

    let model_dir = WalkDir::new(model_dir).min_depth(1).max_depth(1);
    let mut models = vec![];
    for model_entry in model_dir.into_iter() {
        let path = model_entry.unwrap().into_path();
        if path.is_dir() {
            let model = SModelBuilderFilePerRootPersistency::build_model(path, language_builder, model_builder_cache);
            models.push(model)
        } else {
            println!("ERROR: model entry {} is a file not a directory. Cannot be parsed as only file per root persistency is supported.", path.to_str().unwrap().to_string())
        }
    }

    solution.models.extend(models);
    println!("Building from solution {} - {}ms", solution.name, now.elapsed().as_millis());

    return solution;
}

fn extract_solution_core_info<'a>(path_to_msd_file: String) -> SSolution {
    //let solution_file = SolutionFile::new(&path_to_msd_file);

    let file = std::fs::File::open(path_to_msd_file.clone());  
    let mut s = String::new();
    let _ = file.unwrap().read_to_string(&mut s);
    let parse_res = roxmltree::Document::parse(&s);
    let document = parse_res.unwrap();

    let model_element = document.root_element();
    let name = model_element.attributes().find(|a| a.name() == "name").unwrap().value().to_string();
    let uuid = model_element.attributes().find(|a| a.name() == "uuid").unwrap().value().to_string();
    return SSolution::new(name, uuid, path_to_msd_file.clone());
}

#[cfg(test)]
mod tests {
    use crate::builder::ssolution_builder::extract_solution_core_info;
    
    #[test]
    fn test_extract_core_info() {
        // given
        let path_to_msd_file = "../mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_top/mps.cli.lanuse.library_top.msd".to_string();

        //when
        let solution = extract_solution_core_info(path_to_msd_file);

        //assert
        assert_eq!(solution.name, "mps.cli.lanuse.library_top");
        assert_eq!(solution.uuid, "f1017d72-b2a4-4f19-9b27-1327f37f5b09");
    }
}