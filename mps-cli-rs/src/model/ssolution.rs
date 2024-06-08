use std::{cell::RefCell, rc::Rc};

use crate::model::smodel::SModel;

pub struct SSolution {
    pub name: String,
    pub uuid: String,
    pub path_to_module_file: String,
    pub models: Vec<Rc<RefCell<SModel>>>,
}

impl SSolution {
    pub fn new(name: String, uuid: String, path_to_module_file: String) -> Self {
        SSolution {
            name,
            uuid,
            path_to_module_file,
            models: vec![],
        }
    }

    #[allow(dead_code)]
    pub fn find_model(&self, name : &str) -> Option<Rc<RefCell<SModel>>> {
        let model = self.models.iter().find(|m| m.borrow().name == name);
        if let Some(model) = model {            
            return Some(Rc::clone(model));
        }
        None
    }
}