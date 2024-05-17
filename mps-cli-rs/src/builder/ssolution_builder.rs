use std::borrow::BorrowMut;
use std::path::PathBuf;
use std::time::Instant;

use quick_xml::events::Event;
use quick_xml::name::QName;
use quick_xml::Reader;
use walkdir::WalkDir;

use crate::builder::builder_helper::convert_to_string;
use crate::builder::builder_helper::panic_read_file;
use crate::builder::smodel_builder_file_per_root_persistency::SModelBuilderFilePerRootPersistency;
use crate::builder::slanguage_builder::SLanguageBuilder;
use crate::model::ssolution::SSolution;

use super::smodel_builder_file_per_root_persistency::SModelBuilderCache;

pub fn build_solution<'a>(path_buf_to_msd_file: &PathBuf, language_builder : &'a SLanguageBuilder, model_builder_cache : &'a SModelBuilderCache) -> SSolution<'a> {
    let now = Instant::now();
    
    let path_to_msd_file = convert_to_string(&path_buf_to_msd_file);
    let mut solution: SSolution = extract_solution_core_info(path_to_msd_file);
    let solution_dir = path_buf_to_msd_file.parent().unwrap();
    let model_dir = convert_to_string(&solution_dir.to_path_buf()) + "/models";

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
    println!("Building from solution {} - {}ms", solution.name, now.elapsed().as_millis);

    return solution;
}

fn extract_solution_core_info<'a>(path_to_msd_file: String) -> SSolution<'a> {
    //let solution_file = SolutionFile::new(&path_to_msd_file);
    let mut msd_file_reader = Reader::from_file(&path_to_msd_file).unwrap();
    let mut buf = Vec::new();
    let mut name: String = "".to_string();
    let mut uuid: String = "".to_string();
    loop {
        match msd_file_reader.read_event_into(&mut buf) {
            Ok(Event::Start(e)) => {
                match e.name().as_ref() {
                    b"solution" => {
                        for attribute in e.attributes() {
                            let attribute = attribute.unwrap();
                            match attribute.key {
                                QName(b"name") => { name = attribute.unescape_value().unwrap().to_string() }
                                QName(b"uuid") => { uuid = attribute.unescape_value().unwrap().to_string() }
                                QName(_) => {}
                            }
                        }
                        break;
                    }
                    _ => {}
                }
            }
            Err(e) => panic_read_file(&mut msd_file_reader, e),
            _ => {}
        }
    }
    return SSolution::new(name, uuid, path_to_msd_file.clone());
}

#[cfg(test)]
mod tests {
    use crate::builder::builder_helper::convert_to_string;
    use crate::builder::smodules_repository_builder::find_msd_files;
    use crate::builder::ssolution_builder::extract_solution_core_info;
    use crate::builder::test_helper::{get_path_to_mps_cli_lanuse_file_per_root, get_path_to_mps_cli_lanuse_library_top_msd_file};

    #[test]
    fn test_extract_core_info() {
        // given
        let path_to_msd_file = get_path_to_mps_cli_lanuse_library_top_msd_file();

        //when
        let solution = extract_solution_core_info(path_to_msd_file);

        //assert
        assert_eq!(solution.name, "mps.cli.lanuse.library_top");
        assert_eq!(solution.uuid, "f1017d72-b2a4-4f19-9b27-1327f37f5b09");
    }

    #[test]
    fn smoke_test_extract_core_info_for_solutions() {
        //given
        let path_to_test_project = get_path_to_mps_cli_lanuse_file_per_root();

        use std::time::Instant;
        let now = Instant::now();
        //when
        let msd_files = find_msd_files(&path_to_test_project, 3);
        let mut solutions = vec![];
        for msd_file in &msd_files {
            let solution = extract_solution_core_info(convert_to_string(&msd_file));
            solutions.push(solution);
        }

        //then
        println!("Found {} msd files and parsed them in {} solutions in {} ms", msd_files.len(), solutions.len(), now.elapsed().as_millis());
        assert!(msd_files.len() > 1);
        assert!(solutions.len() > 1);
    }
}