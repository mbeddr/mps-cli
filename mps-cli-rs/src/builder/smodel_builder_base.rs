use std::collections::HashMap;
use std::{cell::RefCell, rc::Rc};
use roxmltree::Document;

use crate::model::smodel::SModel;
use crate::model::sconcept::{SConcept, SContainmentLink, SProperty, SReferenceLink};

pub(crate) struct SModelBuilderCache {
    pub index_2_concept: HashMap<String, Rc<SConcept>>,
    pub index_2_property: HashMap<String, Rc<SProperty>>,
    pub index_2_containment_link: HashMap<String, Rc<SContainmentLink>>,
    pub index_2_reference_link: HashMap<String, Rc<SReferenceLink>>,
    pub index_2_imported_model_uuid: HashMap<String, String>,
    pub index_2_model : HashMap<String, Rc<RefCell<SModel>>>,
}

impl SModelBuilderCache {
    pub(crate) fn new() -> Self {
        SModelBuilderCache {
            index_2_concept : HashMap::new(),
            index_2_property : HashMap::new(),
            index_2_containment_link : HashMap::new(),
            index_2_reference_link : HashMap::new(),
            index_2_imported_model_uuid : HashMap::new(),
            index_2_model : HashMap::new(),
         }
    }

    fn get_model(&mut self, name : String, uuid : String) -> Rc<RefCell<SModel>> {        
        if let Some(model) = self.index_2_model.get(&uuid) { 
            Rc::clone(&model) 
        } else {
            let temp = Rc::new(RefCell::new(SModel::new(name.clone(), uuid.clone())));
            self.index_2_model.insert(uuid, temp.clone());
            temp.clone()  
        }
    }
}

pub(crate) fn do_extract_model_core_info(document: Document, model_builder_cache: &mut SModelBuilderCache, path_to_model_file: String) -> Rc<RefCell<SModel>> {
    let model_element = document.root_element();
    let uuid_and_name = model_element.attributes().find(|a| a.name() == "ref").unwrap().value().to_string();

    let left_parens_pos = uuid_and_name.find('(').unwrap();
    let right_parens_pos = uuid_and_name.find(')').unwrap();
    let uuid = uuid_and_name[0..left_parens_pos].to_string();
    let name = uuid_and_name[left_parens_pos + 1..right_parens_pos].to_string();

    let mut is_do_not_generate = false;
    let model_attributes_elements = model_element.children().filter(|c| (c.tag_name().name().to_string() == "attribute"));
    let do_not_generate_attribute = (model_attributes_elements.clone()).find(|a| a.attributes().find(|aa| aa.value() == "doNotGenerate").is_some());
    if let Some(do_not_generate_attribute) = do_not_generate_attribute {
        let do_not_generate_str = do_not_generate_attribute.attributes().find(|aa| aa.name() == "value").unwrap().value();        
        if do_not_generate_str == "true" { is_do_not_generate = true; }                                                        
    }
          
    let my_model = model_builder_cache.get_model(name, uuid);
    my_model.as_ref().borrow_mut().path_to_model_file = path_to_model_file;
    my_model.as_ref().borrow_mut().is_do_not_generate = is_do_not_generate;
    my_model.as_ref().borrow_mut().is_file_per_root_persistency = true;

    let imports = model_element.children().find(|c| c.tag_name().name() == "imports").unwrap();
    for import in imports.children() {
        let tag_name = import.tag_name();
        if tag_name.name() == "import" {
            let uuid_att = import.attributes().find(|a| a.name() == "ref").unwrap().value();

            let uuid = uuid_att.to_string()[0..uuid_att.find('(').unwrap()].to_string();
            let name = uuid_att.to_string()[uuid_att.find('(').unwrap()+1..uuid_att.find(')').unwrap()].to_string();
            let imported_model = model_builder_cache.get_model(name, uuid);
            my_model.as_ref().borrow_mut().imported_models.push(imported_model.clone());
        }
    }

    my_model.clone()
}