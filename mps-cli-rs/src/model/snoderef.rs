use crate::model::snode::SNode;
use crate::model::srepository::SRepository;
use std::rc::Rc;

pub struct SNodeRef {
    pub model_id: String,
    pub node_id: String,
    pub resolve_info: String,
    pub referenced_node : Option<Rc<SNode>>,
}

impl SNodeRef {
    pub fn new(model_id: String, node_id: String, resolve_info: String) -> Self {
        SNodeRef {
            model_id,
            node_id,
            resolve_info,
            referenced_node : None,
        }
    }

    pub fn resolve(&self, repository: &SRepository) -> Option<Rc<SNode>> {
        if self.referenced_node.is_some() {
            return self.referenced_node.clone();
        }

        return match repository.get_model_by_uuid(self.model_id.as_str()) {
            None => None,
            Some(model) => 
                if let Some(n) = model.borrow().get_node_by_id(self.node_id.as_str()) {
                    return Some(n);
                } else {
                    return None;
                }
        };
    }
}