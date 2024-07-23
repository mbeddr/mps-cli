mod model;
mod builder;

use crate::builder::smodules_repository_builder::build_repo_from_directory;

fn main() {
    let repository = build_repo_from_directory(String::from("C:\\work\\E3_2.0_Solution\\solutions"));
    println!("number of solutions: {}", repository.solutions.len());
}


/* 
use std::{path::PathBuf, time::Instant};
use std::io::Read;
use roxmltree::{Document, Node, ParsingOptions};
use std::rc::Rc;
use std::cell::RefCell;

use walkdir::{DirEntry, WalkDir};

fn main() {
    let repo_dir = WalkDir::new("C:\\work\\E3_2.0_Solution\\solutions").min_depth(1).max_depth(10);
    
    let initial_timestamp = Instant::now();
    let mpsr_files : Vec<DirEntry> = repo_dir.into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.clone().into_path().is_file())
        .filter(|f| f.file_name().to_str().unwrap().ends_with(".mpsr"))
        .collect();
    let files_collected_timestamp = Instant::now();
    println!("{} files collected in {}ms", mpsr_files.len(), files_collected_timestamp.duration_since(initial_timestamp).as_millis());

    for file in mpsr_files.iter() {
        let file = std::fs::File::open(file.path());  
        let mut s = String::new();
        let _ = file.unwrap().read_to_string(&mut s);
        let parse_res = roxmltree::Document::parse(&s);
    };
    println!("{} files parsed in {}ms", mpsr_files.len(), Instant::now().duration_since(files_collected_timestamp).as_millis());

}*/