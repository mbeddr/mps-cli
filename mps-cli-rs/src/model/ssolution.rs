use uuid::Uuid;
use crate::model::smodel::SModel;

pub struct SSolution<'a> {
    pub name: String,
    uuid: Uuid,
    path_to_module_file: String,
    models: Vec<SModel<'a>>
}