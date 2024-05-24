use crate::model::snode::SNode;
use crate::model::srepository::SRepository;
use std::rc::Rc;

pub struct SNodeRef {
    pub to: String,
    pub resolve_info: String,
    referenced_node : Option<Rc<SNode>>,
}

impl SNodeRef {
    pub fn new(to: String, resolve_info: String) -> Self {
        SNodeRef {
            to,
            resolve_info,
            referenced_node : None,
        }
    }

    pub fn resolve(&self, repository: &SRepository) -> Option<Rc<SNode>> {
        /*if self.referenced_node.is_some() {
            return self.referenced_node.clone();
        }*/


        /*return match repository.get_model_by_uuid(&self.model_uuid) {
            None => None,
            Some(model) => 
                if let Some(n) = model.get_node_by_uuid(&self.node_uuid) {
                    return Some(n);
                } else {
                    return None;
                }
        };*/
        //let model = repository.get_model_by_uuid(&self.model_uuid).unwrap();
        //model.get_node_by_uuid(&self.node_uuid);
        None
    }
}