use crate::model::sconcept::SConcept;
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Clone)]
pub struct SLanguage {
    pub name: String,
    pub id: String,
    pub concepts: RefCell<Vec<Rc<SConcept>>>,
}

impl SLanguage {
    pub fn new(name: String, id: String) -> Self {
        SLanguage {
            name,
            id,
            concepts: RefCell::new(vec![]),
        }
    }
}
