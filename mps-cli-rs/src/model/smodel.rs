use crate::model::snode::SNode;

pub struct SModel<'a> {
    pub name: String,
    pub uuid: String,
    pub root_nodes: Vec<SNode<'a>>,
    pub path_to_model_file: String,
    pub is_do_not_generate: bool,
    pub is_file_per_root_persistency: bool,
}

impl<'a> SModel<'a> {
    pub fn new(name: String, uuid: String, path_to_model_file: String, is_do_not_generate: bool, is_file_per_root_persistency: bool) -> Self {
        SModel {
            name,
            uuid,
            root_nodes: vec![],
            path_to_model_file,
            is_do_not_generate,
            is_file_per_root_persistency,
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

    pub fn get_node_by_uuid(&self, uuid: &String) -> Option<&SNode> {
        self.get_nodes().iter().find(|&node| node.uuid.eq(uuid)).copied()
    }
}
