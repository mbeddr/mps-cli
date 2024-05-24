use std::collections::HashMap;

use std::cell::RefCell;
use std::rc::Rc;

#[derive(Debug, PartialEq, Clone)]
pub struct SConcept {
    pub name: String,
    pub id: String,
    pub properties: RefCell<HashMap<String, Rc<SProperty>>>,
    pub containment_links: RefCell<HashMap<String, Rc<SContainmentLink>>>,
    pub reference_links: RefCell<HashMap<String, Rc<SReferenceLink>>>,
}

#[derive(PartialEq, Eq, Hash, Debug, Clone)]
pub struct SProperty {
    pub(crate) name: String,
    pub id: String,
}

#[derive(PartialEq, Eq, Hash, Debug, Clone)]
pub struct SContainmentLink {
    pub(crate) name: String,
    id: String,
}

#[derive(PartialEq, Eq, Hash, Debug, Clone)]
pub struct SReferenceLink {
    pub(crate) name: String,
    id: String,
}

impl SConcept {
    pub fn new(name: String, id: String) -> Self {
        SConcept {
            name: name.to_string(),
            id,
            properties: RefCell::new(HashMap::new()),
            containment_links: RefCell::new(HashMap::new()),
            reference_links: RefCell::new(HashMap::new()),
        }
    }

    pub fn print_concept_details(&self) {
        let properties_string_vector: Vec<String> = self.properties.borrow().iter().map(|prop| format!("{} {}", prop.0, prop.1.name)).collect();
        let properties_info = properties_string_vector.join(", ");
        let children_info = self.containment_links.borrow().iter().map(|child| { format!("{} {}", child.0, child.1.name) }).collect::<Vec<_>>().join(", ");
        let reference_info = self.reference_links.borrow().iter().map(|reference| format!("{} {}", reference.0, reference.1.name)).collect::<Vec<_>>().join(", ");
        println!("concept {}\n\
        properties: \n\
        \t\t{}\n\
        children: \n\
        \t\t{}\n\
        references: \n\
        \t\t{}\n\
        <<<", self.name, properties_info, children_info, reference_info);
    }
}

impl SProperty {
    pub fn new(name: String, id: String) -> Self {
        SProperty {
            name,
            id,
        }
    }
}

impl SContainmentLink {
    pub fn new(name: String, id: String) -> Self {
        SContainmentLink {
            name,
            id,
        }
    }
}

impl SReferenceLink {
    pub fn new(name: String, id: String) -> Self {
        SReferenceLink {
            name,
            id,
        }
    }
}