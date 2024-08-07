use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::Rc;

use crate::model::sconcept::{SConcept, SContainmentLink, SProperty, SReferenceLink};
use crate::model::slanguage::SLanguage;


pub(crate) struct SLanguageBuilder {
    pub concept_id_to_concept : RefCell<HashMap<String, Rc<SConcept>>>,
}

impl<'a> SLanguageBuilder {
    pub(crate) fn new() -> Self {
        SLanguageBuilder {
            concept_id_to_concept: RefCell::new(HashMap::new()),
        }
    }

    pub(crate) fn get_or_create_concept(&self, language: &mut SLanguage, concept_id: &str, concept_name: &str) -> Rc<SConcept> {        
        let mut concept_id_to_concept = self.concept_id_to_concept.borrow_mut();
        let concept = concept_id_to_concept.get(concept_id);
        if let Some(c) = concept {
            return Rc::clone(c);
        }
       
        let concept = SConcept::new(concept_name.to_string(), concept_id.to_string());
        let rc = Rc::new(concept);
        concept_id_to_concept.insert(concept_id.to_string(), rc.clone());
        language.concepts.push(rc.clone());
        rc
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

pub(crate) fn get_or_build_language<'a>(language_id: &String, language_name: &String, language_id_to_slanguage: &'a mut HashMap<String, SLanguage>) -> &'a mut SLanguage {
    language_id_to_slanguage.entry(language_id.to_string()).or_insert_with(|| SLanguage::new(language_name.to_string(), language_id.to_string()))
}