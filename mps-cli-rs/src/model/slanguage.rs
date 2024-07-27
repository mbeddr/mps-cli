use crate::model::sconcept::SConcept;
use std::cell::RefCell;
use std::rc::Rc;

pub struct SLanguage {
    pub name: String,
    pub id: String,
    pub concepts: Vec<Rc<SConcept>>,
}

impl SLanguage {
    pub fn new(name: String, id: String) -> Self {
        SLanguage {
            name,
            id,
            concepts: vec![],
        }
    }
}
