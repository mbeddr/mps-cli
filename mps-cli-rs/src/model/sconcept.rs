use std::collections::HashMap;

use uuid::Uuid;

#[derive(Debug, PartialEq)]
pub struct SConcept {
    pub(crate) name: String,
    uuid: Uuid,
    pub(crate) properties: HashMap<String, SProperty>,
    containment_links: HashMap<String, SContainmentLink>,
    reference_links: HashMap<String, SReferenceLink>,
}

#[derive(PartialEq, Eq, Hash, Debug)]
pub struct SProperty {
    pub(crate) name: String,
    uuid: Uuid,
}

#[derive(PartialEq, Eq, Hash, Debug)]
pub struct SContainmentLink {
    pub(crate) name: String,
    uuid: Uuid,
}

#[derive(PartialEq, Eq, Hash, Debug)]
pub struct SReferenceLink {
    pub(crate) name: String,
    uuid: Uuid,
}

impl SConcept {
    pub fn new(name: String, uuid: Uuid) -> Self {
        SConcept {
            name,
            uuid,
            properties: HashMap::new(),
            containment_links: HashMap::new(),
            reference_links: HashMap::new(),
        }
    }

    pub fn print_concept_details(&self) {
        let properties_string_vector: Vec<String> = self.properties.iter().map(|prop| format!("{} {}", prop.0, prop.1.name)).collect();
        let properties_info = properties_string_vector.join(", ");
        let children_info = self.containment_links.iter().map(|child| { format!("{} {}", child.0, child.1.name) }).collect::<Vec<_>>().join(", ");
        let reference_info = self.reference_links.iter().map(|reference| format!("{} {}", reference.0, reference.1.name)).collect::<Vec<_>>().join(", ");
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
    pub fn new(name: String, uuid: Uuid) -> Self {
        SProperty {
            name,
            uuid,
        }
    }
}

impl SContainmentLink {
    pub fn new(name: String, uuid: Uuid) -> Self {
        SContainmentLink {
            name,
            uuid,
        }
    }
}

impl SReferenceLink {
    pub fn new(name: String, uuid: Uuid) -> Self {
        SReferenceLink {
            name,
            uuid,
        }
    }
}

#[cfg(test)]
mod tests {
    use uuid::Uuid;

    use crate::model::sconcept::{SConcept, SContainmentLink, SProperty, SReferenceLink};

    #[test]
    fn test_sconcept() {
        // given
        let mut sconcept: SConcept = SConcept::new("FirstConcept".to_string(), Uuid::new_v4());
        let sproperty = SProperty::new("FirstProperty".to_string(), Uuid::new_v4());
        let reference_link = SReferenceLink::new("FirstLink".to_string(), Uuid::new_v4());
        let containment_link_1 = SContainmentLink::new("FirstContainment".to_string(), Uuid::new_v4());
        let containment_link_2 = SContainmentLink::new("SecondContainment".to_string(), Uuid::new_v4());

        //when
        sconcept.properties.insert("property".to_string(), sproperty);
        sconcept.reference_links.insert("ref".to_string(), reference_link);
        sconcept.containment_links.insert("child1".to_string(), containment_link_1);
        sconcept.containment_links.insert("child2".to_string(), containment_link_2);

        //assert
        assert_eq!(sconcept.properties.len(), 1);
        assert_eq!(sconcept.reference_links.len(), 1);
        assert_eq!(sconcept.containment_links.len(), 2);
    }
}