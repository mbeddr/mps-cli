use std::path::PathBuf;
use std::time::Instant;

use walkdir::WalkDir;
use std::rc::Rc;

use crate::builder::slanguage_builder::SLanguageBuilder;
use crate::builder::smodel_builder_file_per_root_persistency::SModelBuilderCache;
use crate::builder::ssolution_builder::build_solution;
use crate::model::srepository::SRepository;
use crate::model::ssolution::SSolution;
use crate::model::slanguage::SLanguage;

pub fn build_repo_from_directories<'a>(source_dirs: Vec<String>, language_builder : &'a SLanguageBuilder, model_builder_cache : &'a SModelBuilderCache<'a>) -> SRepository<'a> {
    let mut all_solutions : Vec<Rc<SSolution>> = Vec::new();

    for source_dir in source_dirs {
        println!("loading models from directory: {}", source_dir);
        let solutions = build_solutions_from(source_dir, &language_builder, model_builder_cache);
        solutions.into_iter().for_each(|s| all_solutions.push(Rc::new(s)));
    }
    let mut languages: Vec<Rc<SLanguage>> = Vec::new();
    language_builder.language_id_to_slanguage.borrow().values().for_each(|v| languages.push(Rc::clone(v)));
    SRepository::new(all_solutions, languages)
}


pub fn build_repo_from_directory<'a>(source_dir: String, language_builder : &'a SLanguageBuilder, model_builder_cache : &'a SModelBuilderCache<'a>) -> SRepository<'a> {
    let mut all_solutions : Vec<Rc<SSolution>> = Vec::new();
    let solutions = build_solutions_from(source_dir, language_builder, model_builder_cache);
    solutions.into_iter().for_each(|s| all_solutions.push(Rc::new(s)));

    let mut languages: Vec<Rc<SLanguage>> = Vec::new();
    language_builder.language_id_to_slanguage.borrow().values().for_each(|v| languages.push(Rc::clone(v)));
    SRepository::new(all_solutions, languages)
}

fn build_solutions_from<'a>(source_dir: String, language_builder : &'a SLanguageBuilder, model_builder_cache : &'a SModelBuilderCache<'a>) -> Vec<SSolution<'a>> {
    let now = Instant::now();
    let solutions = collect_modules_from_sources(source_dir.clone(), language_builder, model_builder_cache);
    let elapsed = now.elapsed();
    println!("{} milli seconds for handling {}", elapsed.as_millis(), source_dir);

    return solutions;
}

pub fn collect_modules_from_sources<'a>(source_dir: String, language_builder : &'a SLanguageBuilder, model_builder_cache : &'a SModelBuilderCache<'a>) -> Vec<SSolution<'a>> {
    let msd_files = find_msd_files(&source_dir, 3);
    let solutions: Vec<SSolution> = msd_files.iter().map(|msd_file| build_solution(msd_file, language_builder, &model_builder_cache)).collect();
    return solutions;
}

pub fn find_msd_files(source_dir: &String, start_depth: usize) -> Vec<PathBuf> {
    let walk_dir: WalkDir = WalkDir::new(source_dir).max_depth(start_depth);
    let mut msd_files = Vec::new();
    for entry in walk_dir.into_iter() {
        let dir_entry = entry.unwrap();
        let path_buf = dir_entry.into_path();
        if let Some(ext) = path_buf.extension() {
            if ext == "msd" {
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

    use crate::builder::slanguage_builder::SLanguageBuilder;
    use crate::builder::smodel_builder_file_per_root_persistency::SModelBuilderCache;
    use crate::builder::smodules_repository_builder::{build_repo_from_directory, find_msd_files};
    use crate::builder::test_helper::get_path_to_mps_cli_lanuse_file_per_root;
    use crate::model::smodel::SModel;

    #[test]
    fn test_find_msd_files() {
        //given
        let src_dir = get_path_to_mps_cli_lanuse_file_per_root();

        //when
        let msd_files = find_msd_files(&src_dir, 3);

        //then
        assert_eq!(msd_files.len(), 2);
    }

    #[test]
    fn smoke_test_build_repo_from() {
        //given
        let src_dir = get_path_to_mps_cli_lanuse_file_per_root();

        use std::time::Instant;
        let now = Instant::now();
        //when
        let language_builder = SLanguageBuilder::new();
        let model_builder_cache = SModelBuilderCache::new();
        let repository = build_repo_from_directory(src_dir, &language_builder, &model_builder_cache);

        //then
        let required_time = now.elapsed().as_millis();
        let solutions = repository.solutions.borrow();
        let models: Vec<&Rc<RefCell<SModel>>> = solutions.iter().flat_map(|solution| &solution.models).collect();
        let do_not_gen_models: Vec<&&Rc<RefCell<SModel>>> = models.iter().filter(|&model| model.as_ref().borrow().is_do_not_generate).collect();
        let number_of_solutions = repository.solutions.borrow().len();
        println!("Found {} solutions with {} models (out of which {} are set to do not generate) in {} ms", number_of_solutions, models.len(), do_not_gen_models.len(), required_time);
        assert!(number_of_solutions > 1);
        assert!(models.len() > 1);
        assert_eq!(do_not_gen_models.len(), 1);
    }
}