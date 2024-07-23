use std::collections::HashMap;

use crate::model::sconcept::{SConcept, SContainmentLink, SProperty, SReferenceLink};
use crate::model::snoderef::SNodeRef;
use std::rc::Rc;
use std::cell::RefCell;

pub struct SNode {
    pub id: String,
    pub concept: Rc<SConcept>,
    pub role_in_parent: Option<String>,
    properties: HashMap<Rc<SProperty>, String>,
    children: RefCell<HashMap<Rc<SContainmentLink>, Vec<Rc<SNode>>>>,
    references: HashMap<Rc<SReferenceLink>, Rc<SNodeRef>>,
    pub parent: Option<Rc<SNode>>,
}

impl SNode {
    pub fn new(id: String, concept: Rc<SConcept>, role_in_parent: Option<String>) -> Self {
        SNode {
            id,
            concept,
            role_in_parent,
            properties: HashMap::new(),
            children: RefCell::new(HashMap::new()),
            references: HashMap::new(),
            parent: None,
        }
    }

    pub fn add_property(&mut self, property: &Rc<SProperty>, value: String) {
        self.properties.insert(Rc::clone(property), value);
    }

    pub fn get_property(&self, property_name: &str) -> Option<String> {        
        let entry = self.properties.iter().find(|it| it.0.name.eq(property_name));
        return match entry {
            Some(key_val) => { Some(String::clone(key_val.1)) }
            None => None
        }
    }

    pub fn add_reference(&mut self, reference_link: &Rc<SReferenceLink>, model_id : String, node_id : String, resolve : Option<String>) {
        self.references.insert(Rc::clone(reference_link), Rc::new(SNodeRef::new(model_id, node_id, resolve.unwrap_or("".to_string()))));
    }

    pub fn get_reference(&self, ref_role_name: &str) -> Option<Rc<SNodeRef>> {        
        let entry = self.references.iter().find(|it| it.0.name.eq(ref_role_name));
        match entry {
            Some(e) => Some(e.1.clone()),
            None => None
        }
    }

    pub fn add_child(&self, cl: Rc<SContainmentLink>, node: Rc<SNode>) {
        let mut children = self.children.borrow_mut();
        let vec = children.entry(Rc::clone(&cl)).or_insert(Vec::new());
        vec.push(Rc::clone(&node));
    }

    pub fn get_children(&self, child_role_name: &str) -> Vec<Rc<SNode>> {
        let children = self.children.borrow();
        let entry = children.iter().find(|it| it.0.name.eq(child_role_name));
        match entry {
            Some(e) => e.1.clone(),
            None => Vec::new()
        }
    }

    pub fn set_parent(&mut self, parent : Rc<SNode>) {
        self.parent = Some(parent);
    }    

    pub fn get_descendants(node : Rc<SNode>, include_self: bool) -> Vec<Rc<SNode>> {
        let mut descendants: Vec<Rc<SNode>> = Vec::new();
        if include_self { descendants.push(Rc::clone(&node)) }
        Self::get_descendants_internal(node, &mut descendants);
        return descendants;
    }

    fn get_descendants_internal(node : Rc<SNode>, descendants: &mut Vec<Rc<SNode>>) {        
        let children = node.children.borrow();
        let vectors_of_children : Vec<&Rc<SNode>> = children.values().flatten().collect();
        for child in vectors_of_children {            
            descendants.push(Rc::clone(child));
            Self::get_descendants_internal(Rc::clone(child), descendants);
        }
    }
}