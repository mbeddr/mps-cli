use std::collections::HashMap;

use uuid::Uuid;

use crate::model::sconcept::{SConcept, SContainmentLink, SProperty, SReferenceLink};

pub struct SNode<'a> {
    pub(crate) uuid: Uuid,
    concept: &'a SConcept,
    role_in_parent: Option<String>,
    properties: HashMap<&'a SProperty, String>,
    children: HashMap<&'a SContainmentLink, Vec<SNode<'a>>>,
    references: HashMap<&'a SReferenceLink, &'a SNode<'a>>,
    parent: Option<&'a SNode<'a>>,
}

impl<'a> SNode<'a> {
    pub fn new(uuid: Uuid, concept: &'a SConcept, role_in_parent: Option<String>) -> Self {
        SNode {
            uuid,
            concept,
            role_in_parent,
            properties: HashMap::new(),
            children: HashMap::new(),
            references: HashMap::new(),
            parent: None,
        }
    }

    pub fn get_property(&self, property_name: &String) -> Option<&String> {
        return match self.properties.keys().find(|&&key| key.name.eq(property_name)) {
            Some(property) => self.properties.get(property),
            None => None
        };
    }

    pub fn add_property(&mut self, property: &'a SProperty, value: String) {
        self.properties.insert(property, value);
    }

    pub fn add_reference(&mut self, reference: &'a SReferenceLink, referenced_node: &'a SNode<'_>) {
        self.references.insert(reference, referenced_node);
    }

    pub fn get_reference(&self, name: &String) -> Option<&&SNode> {
        return match self.references.keys().find(|&&refLink| refLink.name.eq(name)) {
            None => None,
            Some(reference_link) => self.references.get(reference_link)
        };
    }

    pub fn get_children(&self, name: &String) -> Option<&Vec<SNode>> {
        return match self.children.keys().find(|&&containmetd_link| containmetd_link.name.eq(name)) {
            None => None,
            Some(containment_link) => self.children.get(containment_link)
        };
    }

    pub fn get_descendants(&self, include_self: bool) -> Vec<&'a SNode> {
        let mut descendants: Vec<&SNode> = Vec::new();
        if include_self { descendants.push(self) }
        self.get_descendants_internal(&mut descendants);
        return descendants;
    }

    fn get_descendants_internal(&'a self, descendants: &mut Vec<&'a SNode<'a>>) {
        for children in self.children.values() {
            descendants.extend(children);
            for child in children {
                child.get_descendants_internal(descendants);
            }
        }
    }
}