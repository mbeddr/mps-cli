use crate::model::smodel::SModel;

pub struct SSolution<'a> {
    pub name: String,
    pub uuid: String,
    path_to_module_file: String,
    pub models: Vec<SModel<'a>>,
}

impl<'a> SSolution<'a> {
    pub fn new(name: String, uuid: String, path_to_module_file: String) -> Self {
        SSolution {
            name,
            uuid,
            path_to_module_file,
            models: vec![],
        }
    }
}