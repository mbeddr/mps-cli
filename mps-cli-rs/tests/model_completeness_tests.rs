
use std::{cell::Ref, rc::Rc};
use mps_cli::model::{smodel::SModel, srepository::SRepository, snode::SNode};

#[cfg(test)]
pub (crate) fn check_model_completeness(repo : &SRepository) {
    //library_first_solution
    let library_first_solution = repo.find_solution_by_name("mps.cli.lanuse.library_top").unwrap();
    assert_eq!(library_first_solution.models.len(), 2);
    assert!(library_first_solution.find_model("mps.cli.lanuse.library_top.authors_top").is_some());
    assert!(library_first_solution.find_model("mps.cli.lanuse.library_top.library_top").is_some());

    let library_top_model = repo.find_model_by_name("mps.cli.lanuse.library_top.library_top").unwrap();
    let library_top_model : Ref<SModel> = library_top_model.try_borrow().ok().unwrap();
    assert_eq!(library_top_model.root_nodes.len(), 2);
    let munich_library_root = library_top_model.root_nodes.first().unwrap();
    assert_eq!(munich_library_root.get_property("name"), Some(String::from("munich_library")));
    assert_eq!(SNode::get_descendants(Rc::clone(munich_library_root), true).len(), 8);
    assert_eq!(munich_library_root.get_children("entities").len(), 4);

    assert_eq!(library_top_model.get_nodes().len(), 9);
    assert_eq!(library_top_model.get_node_by_id("4Yb5JA31NUC").unwrap().get_property("name").unwrap(), "munich_library");


    let munich_library_entities = munich_library_root.get_children("entities");
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
    assert_eq!(mark_twain.model_id, "r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed");
    assert_eq!(mark_twain.node_id, "4Yb5JA31NUv");
    assert!(mark_twain.resolve(repo).is_some());
    
    // library_second_solution
    let library_second_solution = repo.find_solution_by_name("mps.cli.lanuse.library_second").unwrap();
    assert_eq!(library_second_solution.models.len(), 1);

    // languages
    let languages = &repo.languages;
    assert_eq!(languages.len(), 3);
    assert!(languages.iter().find(|l| l.name.eq("mps.cli.landefs.library")).is_some());
    let people_lan = languages.iter().find(|l| l.name.eq("mps.cli.landefs.people"));
    assert!(people_lan.is_some());
    assert_eq!(people_lan.unwrap().id, "a7aaae55-aa5e-4a05-b2d0-013745658efa");
    assert!(languages.iter().find(|l| l.name.eq("jetbrains.mps.lang.core")).is_some());
}