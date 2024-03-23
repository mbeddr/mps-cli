use crate::model::snode::SNode;
use crate::model::srepository::SRepository;

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

    pub fn resolve<'a>(&'a self, repository: &'a SRepository) -> Option<&SNode> {
        return match repository.get_model_by_uuid(&self.model_uuid) {
            None => None,
            Some(model) => model.get_node_by_uuid(&self.node_uuid)
        };
    }
}