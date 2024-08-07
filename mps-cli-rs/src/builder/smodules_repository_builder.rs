use std::collections::HashMap;
use std::fs::File;
use std::io::Error;
use std::path::PathBuf;
use std::time::Instant;

use walkdir::WalkDir;
use zip::ZipArchive;

use crate::builder::slanguage_builder::SLanguageBuilder;
use crate::builder::smodel_builder_base::SModelBuilderCache;
use crate::builder::ssolution_builder::build_solution;
use crate::model::srepository::SRepository;
use crate::model::ssolution::SSolution;
use crate::model::slanguage::SLanguage;

use super::smodule_builder_from_jars::build_from_jars;

pub(crate) fn build_repo_from_directory<'a>(dir: String) -> SRepository {
    let mut all_solutions : Vec<SSolution> = Vec::new();
    let mut language_builder = SLanguageBuilder::new();
    let mut language_id_to_slanguage : HashMap<String, SLanguage> = HashMap::new(); 

    build_solutions_from(dir, &mut language_id_to_slanguage, &mut language_builder, & mut all_solutions);

    let all_languages = language_id_to_slanguage.into_iter().map(|(_k, lan)| lan).collect();
    SRepository::new(all_solutions, all_languages)
}

fn build_solutions_from<'a>(dir: String, language_id_to_slanguage: &'a mut HashMap<String, SLanguage>, language_builder : &mut SLanguageBuilder, solutions : &'a mut Vec<SSolution>) {
    let now = Instant::now();
    collect_modules(dir.clone(), language_id_to_slanguage, language_builder, solutions);
    let elapsed = now.elapsed();
    println!("{} milli seconds for handling {}", elapsed.as_millis(), dir);
}

fn collect_modules<'a>(dir: String, language_id_to_slanguage: &'a mut HashMap<String, SLanguage>, language_builder : &mut SLanguageBuilder, solutions : &'a mut Vec<SSolution>) {
    let mut model_builder_cache = SModelBuilderCache::new();

    collect_modules_from_source(&dir, language_id_to_slanguage, language_builder, &mut model_builder_cache, solutions);
    collect_modules_from_jars(dir, language_id_to_slanguage, language_builder, &mut model_builder_cache, solutions);
}

pub(crate) fn collect_modules_from_source(dir: &String, language_id_to_slanguage: &mut HashMap<String, SLanguage>, language_builder: &mut SLanguageBuilder, model_builder_cache : &mut SModelBuilderCache, solutions: &mut Vec<SSolution>) {
    let msd_files = find_files_with_extension(dir, "msd");
    msd_files.iter()
            .for_each(|msd_file| {
                let s = build_solution(msd_file, language_id_to_slanguage, language_builder, model_builder_cache);
                solutions.push(s);
            });
}

fn collect_modules_from_jars(dir: String, language_id_to_slanguage: &mut HashMap<String, SLanguage>, language_builder: &mut SLanguageBuilder, model_builder_cache : &mut SModelBuilderCache, solutions: &mut Vec<SSolution>) {
    let jar_files = find_files_with_extension(&dir, "jar");
    let res = build_from_jars(&dir, jar_files, language_id_to_slanguage, language_builder, model_builder_cache);
    match res {
        Ok(mut s) => solutions.append(&mut s),
        Err(err) => println!("error {}", err),
    }
}

fn find_files_with_extension(source_dir: &String, searched_ext : &str) -> Vec<PathBuf> {
    let walk_dir: WalkDir = WalkDir::new(source_dir);
    let mut msd_files = Vec::new();
    for entry in walk_dir.into_iter() {
        let dir_entry = entry.unwrap();
        let path_buf = dir_entry.into_path();
        if let Some(ext) = path_buf.extension() {
            if ext == searched_ext {
                msd_files.push(path_buf)
            }
        }
    }
    return msd_files;
}


#[cfg(test)]
mod tests {   
    use std::cell::RefCell;
    use std::rc::Rc;

    use crate::builder::smodules_repository_builder::{build_repo_from_directory, find_files_with_extension};
    use crate::model::smodel::SModel;

    #[test]
    fn test_find_msd_files() {
        //given
        let src_dir = "../mps_test_projects/mps_cli_lanuse_file_per_root/".to_string();
        //when
        let msd_files = find_files_with_extension(&src_dir, "msd");

        //then
        assert_eq!(msd_files.len(), 2);
    }

    #[test]
    fn smoke_test_build_repo_from() {
        //given
        let src_dir = "../mps_test_projects/mps_cli_lanuse_file_per_root/".to_string();

        use std::time::Instant;
        let now = Instant::now();
        //when
        let repository = build_repo_from_directory(src_dir);

        //then
        let required_time = now.elapsed().as_millis();        
        let models: Vec<&Rc<RefCell<SModel>>> = repository.solutions.iter().flat_map(|solution| &solution.models).collect();
        let do_not_gen_models: Vec<&&Rc<RefCell<SModel>>> = models.iter().filter(|&model| model.as_ref().borrow().is_do_not_generate).collect();
        let number_of_solutions = repository.solutions.len();
        println!("Found {} solutions with {} models (out of which {} are set to do not generate) in {} ms", number_of_solutions, models.len(), do_not_gen_models.len(), required_time);
        assert_eq!(number_of_solutions, 2);
        assert_eq!(models.len(), 3);
        assert_eq!(do_not_gen_models.len(), 1);

        assert!(repository.find_solution_by_name("mps.cli.lanuse.library_top").is_some());
        
        //assert!(repository.get_model_by_uuid("r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed").is_some());
    }
}