use std::path::PathBuf;
use std::time::Instant;

use walkdir::WalkDir;

use crate::builder::ssolution_builder::build_solution;
use crate::model::srepository::SRepository;
use crate::model::ssolution::SSolution;

pub fn build_repo_from_all<'a>(source_dirs: Vec<String>) -> SRepository<'a> {
    let mut all_solutions = Vec::new();
    for source_dir in source_dirs {
        println!("loading models from directory: {}", source_dir);
        let solutions = build_solutions_from(source_dir);
        all_solutions.extend(solutions);
    }
    return SRepository::new(all_solutions, vec![]);
}


pub fn build_repo_from<'a>(source_dir: String) -> SRepository<'a> {
    let solutions = build_solutions_from(source_dir);
    return SRepository::new(solutions, vec![]);
}

fn build_solutions_from<'a>(source_dir: String) -> Vec<SSolution<'a>> {
    let now = Instant::now();

    let solutions = collect_modules_from_sources(source_dir.clone());

    let elapsed = now.elapsed();
    println!("{} milli seconds for handling {}", elapsed.as_millis(), source_dir);

    return solutions;
}

pub fn collect_modules_from_sources<'a>(source_dir: String) -> Vec<SSolution<'a>> {
    let msd_files = find_msd_files(&source_dir, 3);
    let solutions: Vec<SSolution> = msd_files.iter().map(|msd_file| build_solution(msd_file)).collect();
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
    use crate::builder::smodules_repository_builder::{build_repo_from, find_msd_files};
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
        let repository = build_repo_from(src_dir);

        //then
        let required_time = now.elapsed().as_millis();
        let models: Vec<&SModel> = repository.solutions.iter().flat_map(|solution| &solution.models).collect();
        let do_not_gen_models: Vec<&&SModel> = models.iter().filter(|&model| model.is_do_not_generate).collect();
        println!("Found {} solutions with {} models (out of which {} are set to do not generate) in {} ms", repository.solutions.len(), models.len(), do_not_gen_models.len(), required_time);
        assert!(repository.solutions.len() > 1);
        assert!(models.len() > 1);
        assert_eq!(do_not_gen_models.len(), 1);
    }
}