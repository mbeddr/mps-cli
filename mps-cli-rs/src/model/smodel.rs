use crate::model::snode::SNode;
use std::{cell::RefCell, rc::Rc};

pub struct SModel<'a> {
    pub name: String,
    pub uuid: String,
    pub root_nodes: Vec<Rc<SNode<'a>>>,
    pub path_to_model_file: String,
    pub is_do_not_generate: bool,
    pub is_file_per_root_persistency: bool,
    pub imported_models: Vec<Rc<RefCell<SModel<'a>>>>
}

impl<'a> SModel<'a> {
    pub fn new(name: String, uuid: String) -> Self {
        SModel {
            name,
            uuid,
            root_nodes: vec![],
            path_to_model_file : String::from(""),
            imported_models : vec![],
            is_do_not_generate : false,
            is_file_per_root_persistency : false,
        }
    }

    pub fn get_nodes(&'a self) -> Vec<&SNode<'a>> {
        let mut nodes: Vec<&SNode> = Vec::new();
        /*for root in &self.root_nodes {
            nodes.push(root);
            nodes.extend(root.get_descendants(false));
        }*/
        return nodes;
    }

    pub fn get_node_by_id(&'a self, id: &'a String) -> Option<Rc<SNode<'a>>> {
        /*let nodes = self.get_nodes();
        let n = nodes.iter().find(|node| node.id.eq(id));
        if let Some(nn) = n { return Some(Rc::new(**nn)); }
        */None
    }
}
