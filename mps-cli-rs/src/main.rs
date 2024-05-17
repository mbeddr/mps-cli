mod model;
mod builder;

use crate::builder::smodules_repository_builder::build_repo_from_directory;
use crate::builder::slanguage_builder::SLanguageBuilder;
use crate::builder::smodel_builder_file_per_root_persistency::SModelBuilderCache;

fn main() {
    let language_builder = SLanguageBuilder::new();
    let model_builder_cache = SModelBuilderCache::new();
    let repository = build_repo_from_directory(String::from("C:\\work\\E3_2.0_Solution\\solutions"), &language_builder, &model_builder_cache);
    println!("number of solutions: {}", repository.solutions.borrow().len());
}

//160523 milli seconds