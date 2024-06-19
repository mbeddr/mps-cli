pub mod model;
mod builder;

use crate::model::srepository::SRepository;

pub fn build_repo_from_directory(source_dir: String) -> SRepository {
    crate::builder::smodules_repository_builder::build_repo_from_directory(source_dir)
}