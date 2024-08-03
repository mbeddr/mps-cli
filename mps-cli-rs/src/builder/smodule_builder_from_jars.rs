use std::env;
use std::fs::remove_dir_all;
use std::fs;
use std::{collections::HashMap, fs::File, io::Error, path::PathBuf};
use zip::ZipArchive;

use crate::builder::smodules_repository_builder::collect_modules_from_source;
use crate::model::{slanguage::SLanguage, ssolution::SSolution};

use super::slanguage_builder::SLanguageBuilder;
use super::smodel_builder_base::SModelBuilderCache;



pub(crate) fn build_from_jars(dir : &String, jar_files : Vec<PathBuf>, language_id_to_slanguage: &mut HashMap<String, SLanguage>, language_builder : &mut SLanguageBuilder, model_builder_cache : &mut SModelBuilderCache) -> Result<Vec<SSolution>, Error> {
    let mut res = Vec::new();
    let root_path = PathBuf::from(dir);
    let root_path = fs::canonicalize(&root_path)?;
    let temp_dir = env::temp_dir();
    println!("Collecting jars from root path: {}", root_path.display());
    for jar_file in jar_files {
        let archive = File::open(jar_file.clone())?;
        let mut archive = ZipArchive::new(archive)?;
        if !archive.file_names().any(|it| it.ends_with(".msd")) {
            continue;
        }

        let mut absolute_path_to_jar_file = jar_file.canonicalize()?.into_os_string();
        absolute_path_to_jar_file.push("_jar");
        let absolute_path_to_jar_dir = PathBuf::from(absolute_path_to_jar_file.to_str().unwrap());
        let relative_directory_of_jar = absolute_path_to_jar_dir.strip_prefix(root_path.clone()).unwrap();
        let temporary_directory_to_extract_jar = temp_dir.join(relative_directory_of_jar);


        println!(" - extracted '{}' to temporary dir '{}'", jar_file.file_name().unwrap().to_str().unwrap(), temporary_directory_to_extract_jar.to_str().unwrap());
        archive.extract(temporary_directory_to_extract_jar.clone())?;  
        collect_modules_from_source(&temporary_directory_to_extract_jar.to_str().unwrap().to_owned(), language_id_to_slanguage, language_builder, model_builder_cache, &mut res);        
        remove_dir_all(temporary_directory_to_extract_jar.clone())?;
        println!(" - removed dir '{}'", temporary_directory_to_extract_jar.to_str().unwrap());
    };
    Ok(res)        
}