use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::Rc;

use crate::model::sconcept::{SConcept, SContainmentLink, SProperty, SReferenceLink};
use crate::model::slanguage::SLanguage;


pub(crate) struct SLanguageBuilder {
    pub language_id_to_slanguage: RefCell<HashMap<String, Rc<SLanguage>>>,
    pub concept_id_to_concept : RefCell<HashMap<String, Rc<SConcept>>>,
}

impl<'a> SLanguageBuilder {
    pub(crate) fn new() -> Self {
        SLanguageBuilder {
            language_id_to_slanguage: RefCell::new(HashMap::new()),
            concept_id_to_concept: RefCell::new(HashMap::new()),
        }
    }

    pub(crate) fn get_or_build_language(&self, language_id: &String, language_name: &String) -> Rc<SLanguage> {
        let mut l = self.language_id_to_slanguage.borrow_mut();
        let res = l.entry(language_id.to_string()).or_insert_with(|| Rc::new(SLanguage::new(language_name.to_string(), language_id.to_string())));
        Rc::clone(res)
    }

    pub(crate) fn get_or_create_concept(&'a self, language: Rc<SLanguage>, concept_id: String, concept_name: String) -> Rc<SConcept> {
        let mut concepts = language.concepts.borrow_mut();
        if let Some(i) = concepts.iter().position(|c| c.name == concept_name) {
            let c = &concepts[i];
            Rc::clone(c)
        } else {
            concepts.push(Rc::new(SConcept::new(concept_name.clone(), concept_id.clone())));
            Rc::clone(concepts.last().unwrap())
        }
    }


    pub(crate) fn get_or_create_property(&'a self, concept: Rc<SConcept>, property_id: String, property_name: String) -> Rc<SProperty> {
        let mut props = concept.properties.borrow_mut();
        let property = props.entry(property_id.clone()).or_insert(Rc::new(SProperty::new(property_name, property_id)));
        Rc::clone(property)
    }

    pub(crate) fn get_or_create_child(&'a self, concept: Rc<SConcept>, child_id: String, child_name: String) -> Rc<SContainmentLink> {
        let mut links = concept.containment_links.borrow_mut();
        let containment_link = links.entry(child_id.clone()).or_insert(Rc::new(SContainmentLink::new(child_name, child_id)));
        Rc::clone(containment_link)
    }

    pub(crate) fn get_or_create_reference(&'a self, concept: Rc<SConcept>, reference_id: String, reference_name: String) -> Rc<SReferenceLink> {
        let mut refs = concept.reference_links.borrow_mut();
        let reference_link = refs.entry(reference_id.clone()).or_insert(Rc::new(SReferenceLink::new(reference_name, reference_id)));
        Rc::clone(reference_link)
    }

}





