
use std::rc::Rc;
use mps_cli::model::{smodel::SModel, snode::SNode};


pub (crate) fn check_model_completeness(model : &SModel) {
   
    //assert
    let munich_library_root = model.root_nodes.first().unwrap();
    assert_eq!(munich_library_root.get_property("name"), Some(String::from("munich_library")));
    assert_eq!(SNode::get_descendants(Rc::clone(munich_library_root), true).len(), 8);
    assert_eq!(munich_library_root.get_children("entities").len(), 4);

    assert_eq!(model.get_nodes().len(), 9);
    assert_eq!(model.get_node_by_id("4Yb5JA31NUC").unwrap().get_property("name").unwrap(), "munich_library");
}