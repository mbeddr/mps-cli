use uuid::Uuid;

use crate::model::snode::SNode;

pub struct SModel<'a> {
    name: String,
    uuid: Uuid,
    root_nodes: Vec<SNode<'a>>,
    path_to_model_file: String,
    is_do_not_generate: bool,
    is_file_per_root_persistency: bool,
}

impl<'a> SModel<'a> {
    pub fn new(name: String, uuid: Uuid) -> Self {
        SModel {
            name,
            uuid,
            root_nodes: vec![],
            path_to_model_file: "".to_string(),
            is_do_not_generate: false,
            is_file_per_root_persistency: true,
        }
    }

    pub fn get_nodes(&self) -> Vec<&SNode> {
        let mut nodes: Vec<&SNode> = Vec::new();
        for root in &self.root_nodes {
            nodes.push(&root);
            nodes.extend(root.get_descendants(false));
        }
        return nodes;
    }

    pub fn get_node_by_uuid(&self, uuid: &Uuid) -> Option<&SNode> {
        self.get_nodes().iter().find(|&node| node.uuid.eq(uuid)).copied()
    }
}
