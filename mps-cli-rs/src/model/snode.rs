use std::collections::HashMap;

use crate::model::sconcept::{SConcept, SContainmentLink, SProperty, SReferenceLink};
use std::rc::Rc;
use std::cell::RefCell;

pub struct SNodeRef {
    to : String,
    resolve : Option<String>,
}

pub struct SNode<'a> {
    pub id: String,
    pub concept: Rc<SConcept>,
    pub role_in_parent: Option<String>,
    properties: RefCell<HashMap<Rc<SProperty>, String>>,
    children: RefCell<HashMap<Rc<SContainmentLink>, Vec<Rc<SNode<'a>>>>>,
    references: RefCell<HashMap<Rc<SReferenceLink>, Rc<SNodeRef>>>,
    pub parent: RefCell<Option<Rc<SNode<'a>>>>,
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
            parent: RefCell::new(None),
        }
    }

    pub fn add_property(&self, property: &Rc<SProperty>, value: String) {
        self.properties.borrow_mut().insert(Rc::clone(property), value);
    }

    pub fn get_property(&self, property_name: &str) -> Option<String> {
        let properties = self.properties.borrow();
        let entry = properties.iter().find(|it| it.0.name.eq(property_name));
        return match entry {
            Some(key_val) => { Some(String::clone(key_val.1)) }
            None => None
        }
    }

    pub fn add_reference(&self, reference_link: &Rc<SReferenceLink>, to: String, resolve : Option<String>) {
        self.references.borrow_mut().insert(Rc::clone(reference_link), Rc::new(SNodeRef {
            to : to,
            resolve : resolve,
        }));
    }

    pub fn add_child(&self, cl: Rc<SContainmentLink>, node: Rc<SNode<'a>>) {
        let mut children = self.children.borrow_mut();
        let vec = children.entry(Rc::clone(&cl)).or_insert(Vec::new());
        vec.push(Rc::clone(&node));
    }

    pub fn get_children(&self, child_role_name: &str) -> Vec<Rc<SNode<'a>>> {
        let children = self.children.borrow();
        let entry = children.iter().find(|it| it.0.name.eq(child_role_name));
        match entry {
            Some(e) => e.1.clone(),
            None => Vec::new()
        }
    }

    pub fn set_parent(&self, parent : Rc<SNode<'a>>) {
        self.parent.replace(Some(parent));
    }    

    pub fn get_descendants(node : Rc<SNode<'a>>, include_self: bool) -> Vec<Rc<SNode<'a>>> {
        let mut descendants: Vec<Rc<SNode<'a>>> = Vec::new();
        if include_self { descendants.push(Rc::clone(&node)) }
        Self::get_descendants_internal(node, &mut descendants);
        return descendants;
    }

    fn get_descendants_internal(node : Rc<SNode<'a>>, descendants: &mut Vec<Rc<SNode<'a>>>) {        
        let children = node.children.borrow();
        let vectors_of_children : Vec<&Rc<SNode<'a>>> = children.values().flatten().collect();
        for child in vectors_of_children {            
            descendants.push(Rc::clone(child));
            Self::get_descendants_internal(Rc::clone(child), descendants);
        }
    }
}