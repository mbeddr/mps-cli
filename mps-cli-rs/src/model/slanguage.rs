use crate::model::sconcept::SConcept;
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Clone)]
pub struct SLanguage {
    pub name: String,
    pub uuid: String,
    pub concepts: RefCell<Vec<Rc<SConcept>>>,
}

impl SLanguage {
    pub fn new(name: String, uuid: String) -> Self {
        SLanguage {
            name,
            uuid,
            concepts: RefCell::new(vec![]),
        }
    }
}

#[cfg(test)]
mod tests {
    use uuid::Uuid;

    use crate::model::sconcept::SConcept;
    use crate::model::slanguage::SLanguage;

    #[test]
    fn test_find_concept_by_name() {

    }
}