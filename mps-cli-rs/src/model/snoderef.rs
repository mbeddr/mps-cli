use crate::model::snode::SNode;
use crate::model::srepository::SRepository;
use std::rc::Rc;

struct SNodeRef {
    model_uuid: String,
    node_uuid: String,
}

impl SNodeRef {
    pub fn new(model_uuid: String, node_uuid: String) -> Self {
        SNodeRef {
            model_uuid,
            node_uuid,
        }
    }

    pub fn resolve<'a>(&'a self, repository: &'a SRepository<'a>) -> Option<Rc<SNode<'a>>> {
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