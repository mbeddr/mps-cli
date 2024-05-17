use std::{borrow::BorrowMut, collections::HashMap};

use crate::model::sconcept::{SConcept, SContainmentLink, SProperty, SReferenceLink};
use std::rc::Rc;
use std::cell::RefCell;

pub struct SNodeRef {
    to : String,
    resolve : Option<String>,
}

pub struct SNode<'a> {
    pub(crate) id: String,
    concept: Rc<SConcept>,
    role_in_parent: Option<String>,
    properties: RefCell<HashMap<Rc<SProperty>, String>>,
    children: RefCell<HashMap<Rc<SContainmentLink>, Rc<Vec<Rc<SNode<'a>>>>>>,
    references: RefCell<HashMap<Rc<SReferenceLink>, Rc<SNodeRef>>>,
    parent: Option<&'a SNode<'a>>,
}

impl<'a> SNode<'a> {
    pub fn new(id: String, concept: Rc<SConcept>, role_in_parent: Option<String>) -> Self {
        SNode {
            id,
            concept,
            role_in_parent,
            properties: RefCell::new(HashMap::new()),
            children: RefCell::new(HashMap::new()),
            references: RefCell::new(HashMap::new()),
            parent: None,
        }
    }

    pub fn get_property(&self, property_name: &String) -> Option<String> {
        let properties = self.properties.borrow();
        return match properties.keys().find(|&key| key.name.eq(property_name)) {
            Some(property) => { let p = properties.get(property).unwrap().clone(); Some(p) }
            None => None
        };
    }

    pub fn add_property(&self, property: &Rc<SProperty>, value: String) {
        let mut props = self.concept.properties.borrow_mut();
        self.properties.borrow_mut().insert(Rc::clone(property), value);
    }

    pub fn add_reference(&self, reference_link: &Rc<SReferenceLink>, to: String, resolve : Option<String>) {
        self.references.borrow_mut().insert(Rc::clone(reference_link), Rc::new(SNodeRef {
            to : to,
            resolve : resolve,
        }));
    }

    pub fn add_child(&self, cl: Rc<SContainmentLink>, node: Rc<SNode<'a>>) {
        let mut children = self.children.borrow_mut();
        let vec = children.entry(Rc::clone(&cl)).or_insert(Rc::new(Vec::new()));
        Rc::get_mut(vec).unwrap().push(Rc::clone(&node));
    }

    /*pub fn get_children(&self, name: &String) -> Option<&Vec<SNode>> {
        return match self.children.keys().find(|&&containmetd_link| containmetd_link.name.eq(name)) {
            None => None,
            Some(containment_link) => self.children.get(containment_link)
        };
    }*/

    pub fn get_descendants(&'a self, include_self: bool) -> Vec<&SNode> {
        let mut descendants: Vec<&SNode<'a>> = Vec::new();
        if include_self { descendants.push(self) }
        self.get_descendants_internal(&mut descendants);
        return descendants;
    }

    fn get_descendants_internal(&'a self, descendants: &mut Vec<&SNode<'a>>) {
        /*let all_children_entries = self.children.borrow();
        let containment_links = all_children_entries.keys();
        
        for containment_link in containment_links {
            for children in all_children_entries.get(containment_link) {
                for child in children {
                    descendants.push(child.as_ref());
                    child.get_descendants_internal(descendants);
                }
            }
        }*/

    }
}