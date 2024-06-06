mod model_completeness_tests;
use mps_cli::build_repo_from_directory;

#[test]
fn test_build_repository() {
    // given
    let path = "../mps_test_projects/mps_cli_lanuse_file_per_root/";     

    //when
    let repo = build_repo_from_directory(path.to_string());    

    //assert
    assert_eq!(repo.solutions.borrow().len(), 2);

    let library_top_solution = repo.find_solution_by_name("mps.cli.lanuse.library_top").unwrap();
    assert_eq!(library_top_solution.models.len(), 2);
    let library_top_model = library_top_solution.find_model("mps.cli.lanuse.library_top.library_top").unwrap();
    assert_eq!(library_top_model.borrow().root_nodes.len(), 2);
    

    let library_second_solution = repo.find_solution_by_name("mps.cli.lanuse.library_second").unwrap();
    assert_eq!(library_second_solution.models.len(), 1);
    
    let munich_library = library_top_model.borrow().find_root("munich_library");
    assert!(munich_library.is_some());

    let munich_library = munich_library.unwrap();
    let munich_library_entities = munich_library.get_children("entities");
    assert_eq!(munich_library_entities.len(), 4);
    let tom_sawyer = munich_library_entities.first().unwrap();
    assert_eq!(tom_sawyer.get_property("name"), Some(String::from("Tom Sawyer")));
    assert_eq!(tom_sawyer.role_in_parent, Some(String::from("entities")));
    assert_eq!(tom_sawyer.get_property("publicationDate"), Some(String::from("1876")));
    assert_eq!(tom_sawyer.get_property("isbn"), Some(String::from("4323r2")));
    assert_eq!(tom_sawyer.get_property("available"), Some(String::from("true")));
    assert_eq!(tom_sawyer.concept.name, String::from("mps.cli.landefs.library.structure.Book"));

    let authors = tom_sawyer.get_children("authors");
    let mark_twain = authors.first().unwrap().get_reference("person").unwrap();
    assert_eq!(mark_twain.resolve_info, "Mark Twain");
    assert_eq!(mark_twain.to, "q0v6:4Yb5JA31NUv");
}

 
#[test]
fn test_navigate_model() {
    let path = "../mps_test_projects/mps_cli_lanuse_file_per_root/solutions/"; 
    let repo = build_repo_from_directory(path.to_string()); 
    
    let library_top_model = repo.find_model_by_name("mps.cli.lanuse.library_top.library_top").unwrap();
    if let Ok(library_top_model) = library_top_model.try_borrow() {
        model_completeness_tests::check_model_completeness(&library_top_model);
    };
   
}