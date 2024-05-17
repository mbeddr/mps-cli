use std::borrow::{Borrow, BorrowMut};
use std::collections::HashMap;
use std::fs::File;
use std::io::BufReader;
use std::ops::DerefMut;
use std::path::PathBuf;
use std::sync::Mutex;
use std::io::Read;
use roxmltree::{Document, Node};
use std::rc::Rc;
use std::cell::RefCell;

use quick_xml::events::{attributes, Event};
use quick_xml::Reader;
use walkdir::{DirEntry, WalkDir};

use crate::builder::builder_helper::{convert_to_string, get_value_of_attribute_with_key, get_values_of_attributes_with_keys, panic_read_file, panic_unexpected_eof_read_file};
use crate::model::sconcept::{SConcept, SContainmentLink, SProperty, SReferenceLink};
use crate::model::smodel::SModel;
use crate::model::snode::SNode;
use roxmltree::ParsingOptions;
use super::slanguage_builder::SLanguageBuilder;


#[derive(Clone)]
pub struct SModelBuilderCache {
    pub index_2_concept: RefCell<HashMap<String, Rc<SConcept>>>,
    pub index_2_property: RefCell<HashMap<String, Rc<SProperty>>>,
    pub index_2_containment_link: RefCell<HashMap<String, Rc<SContainmentLink>>>,
    pub index_2_reference_link: RefCell<HashMap<String, Rc<SReferenceLink>>>,
    pub index_2_imported_model_uuid: RefCell<HashMap<String, String>>,
}

impl SModelBuilderCache {
    pub fn new() -> Self {
        SModelBuilderCache {
            index_2_concept: RefCell::new(HashMap::new()),
            index_2_property: RefCell::new(HashMap::new()),
            index_2_containment_link : RefCell::new(HashMap::new()),
            index_2_reference_link : RefCell::new(HashMap::new()),
            index_2_imported_model_uuid: RefCell::new(HashMap::new()),
        }
    }
}

pub struct SModelBuilderFilePerRootPersistency {}

impl SModelBuilderFilePerRootPersistency {
    pub(crate) fn new() -> Self {
        SModelBuilderFilePerRootPersistency {}
    }

    pub(crate) fn build_model<'a>(path_to_model: PathBuf, language_builder : &'a SLanguageBuilder, model_builder_cache : &'a SModelBuilderCache) -> SModel<'a> {
        let opt = roxmltree::ParsingOptions {
            allow_dtd: true,
            ..roxmltree::ParsingOptions::default()
        };
        
        let mut model_file = path_to_model.clone();
        model_file.push(".model");

        let path_to_model_file = model_file.to_str().unwrap().to_string();

        let mut model: SModel = Self::extract_model_core_info(model_file, &opt);

        let mpsr_file_walker = WalkDir::new(path_to_model).min_depth(1).max_depth(1);
        let mpsr_files = mpsr_file_walker.into_iter().filter(|entry| {
            if entry.is_ok() {
                let dir_entry = entry.as_ref().unwrap();
                let extension = dir_entry.path().extension();
                return dir_entry.file_type().is_file() && extension.is_some_and(|e| e.eq("mpsr"));
            }
            return false;
        });

        let mut roots = vec!();
        for mpsr_file in mpsr_files.into_iter() {
            let file = mpsr_file.unwrap();
            if let Some(r) = Self::build_root_node_from_file(file, &opt, language_builder, model_builder_cache) {
                roots.push(r);
            }
        };
        model.root_nodes.extend(roots);

        return model;
    }

    fn extract_model_core_info<'a>(path_to_model: PathBuf, opt : &ParsingOptions) -> SModel<'a> {
        let path_to_model_file = path_to_model.to_str().unwrap().to_string();        

        let file = std::fs::File::open(path_to_model_file.clone());  
        let mut s = String::new();
        file.unwrap().read_to_string(&mut s);
        let parse_res = roxmltree::Document::parse(&s);
        let document = parse_res.unwrap();

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
        
        
        return SModel::new(name, uuid, path_to_model_file, is_do_not_generate, true);
    }

    fn build_root_node_from_file<'a>(dir_entry: DirEntry, opt : &ParsingOptions, language_builder : &'a SLanguageBuilder, model_builder_cache : &'a SModelBuilderCache) -> Option<Rc<SNode<'a>>> {        
        //println!("building root node from {}", dir_entry.path().as_os_str().to_str().unwrap());
        let file = std::fs::File::open(dir_entry.path().as_os_str());  

        let mut s = String::new();
        file.unwrap().read_to_string(&mut s);
        let parse_res = roxmltree::Document::parse_with_options(&s, *opt);
        
        let document = parse_res.unwrap();
        Self::parse_imports(&document, model_builder_cache);
        Self::parse_registry(&document, language_builder, model_builder_cache);
        
        let node = document.root_element().children().find(|it| it.tag_name().name() == "node");
        let mut parent: Option<Rc<SNode>> = None;
        Some(Self::parse_node(&mut parent, &node.unwrap(), language_builder, &model_builder_cache))      
    }

    fn parse_imports(document: &Document, model_builder_cache : &SModelBuilderCache) {
        let model_element = document.root_element();
        let imports_element = model_element.children().find(|c| c.tag_name().name() == "imports");
        match imports_element {
            Some(imports) => {
                for import in imports.children() {
                    let tag_name = import.tag_name();
                    if tag_name.name() == "import" {
                        let index = import.attributes().find(|a| a.name() == "index").unwrap().value();
                        let uuid = import.attributes().find(|a| a.name() == "ref").unwrap().value();

                        let uuid = uuid.to_string()[0..uuid.find('(').unwrap()].to_string();
                        model_builder_cache.index_2_imported_model_uuid.borrow_mut().insert(index.to_string(), uuid);
                    }
                }
            },
            _ => ()
        }
    }

    fn parse_registry<'a>(document: &Document, language_builder : &'a SLanguageBuilder, model_builder_cache : &'a SModelBuilderCache) {
        let model_element = document.root_element();
        let registry_element = model_element.children().find(|c| c.tag_name().name() == "registry");
        match registry_element {
            Some(registry) => {
                for language in registry.children() {
                    if language.tag_name().name() != "language" { continue; }
                    
                    let language_id = language.attributes().find(|a| a.name() == "id").unwrap().value();
                    let language_name = language.attributes().find(|a| a.name() == "name").unwrap().value();
                    
                    let lang = language_builder.get_or_build_language(&language_id.to_string(), &language_name.to_string());
                    for concept in language.children() {
                        if concept.tag_name().name() != "concept" { continue; }
                                                
                        let concept_id = concept.attributes().find(|a| a.name() == "id").unwrap().value();
                        let concept_name = concept.attributes().find(|a| a.name() == "name").unwrap().value();
                        let concept_index = concept.attributes().find(|a| a.name() == "index").unwrap().value();
                        let conc = language_builder.get_or_create_concept(Rc::clone(&lang), concept_id.to_string(), concept_name.to_string());
                        model_builder_cache.index_2_concept.borrow_mut().insert(concept_index.to_string(), Rc::clone(&conc));
                       
                        for properties_links_references in concept.children() {
                            if properties_links_references.tag_name().name() == "" { continue; }

                            let tag_name = properties_links_references.tag_name().name();
                            let id = properties_links_references.attributes().find(|a| a.name() == "id").unwrap().value();
                            let name = properties_links_references.attributes().find(|a| a.name() == "name").unwrap().value();
                            let index = properties_links_references.attributes().find(|a| a.name() == "index").unwrap().value();
                            
                            if tag_name == "property" {
                                let prop = language_builder.get_or_create_property(Rc::clone(&conc),id.to_string(), name.to_string());
                                model_builder_cache.index_2_property.borrow_mut().insert(index.to_string(), Rc::clone(&prop));                                    
                            } else if tag_name == "child" {
                                let child_link = language_builder.get_or_create_child(Rc::clone(&conc),id.to_string(), name.to_string());                                    
                                model_builder_cache.index_2_containment_link.borrow_mut().insert(index.to_string(), Rc::clone(&child_link));
                            } else if tag_name == "reference" {
                                let ref_link = language_builder.get_or_create_reference(Rc::clone(&conc),id.to_string(), name.to_string());
                                model_builder_cache.index_2_reference_link.borrow_mut().insert(index.to_string(), Rc::clone(&ref_link));                                    
                            }    
                        }                           
                    }
                };
            },
            _ => ()
        }
    }


    fn parse_node<'a>(parent_node : &mut Option<Rc<SNode<'a>>>, node: &Node, language_builder : &'a SLanguageBuilder, model_builder_cache : &'a SModelBuilderCache) -> Rc<SNode<'a>> {
        let node_attrs = node.attributes();
        let concept_index = (node_attrs.clone()).into_iter().find(|a| a.name() == "concept").unwrap().value();
        let node_id = (node_attrs.clone()).into_iter().find(|a| a.name() == "id").unwrap().value();
        let role = (node_attrs.clone()).into_iter().find(|a| a.name() == "role");
        let role = if role.is_none() { None } else { Some(role.unwrap().value().to_string()) };

        let index_2_concept = model_builder_cache.index_2_concept.borrow();
        
        let my_concept = index_2_concept.get(concept_index).unwrap();
        let mut current_node : Rc<SNode> = Rc::new(SNode::new(node_id.to_string(), Rc::clone(my_concept), role.clone()));
        
        if let Some(parent) = parent_node {
            let index_2_containment_link = model_builder_cache.index_2_containment_link.borrow();
            let cl = index_2_containment_link.get(&role.unwrap());
            parent.borrow_mut().add_child(Rc::clone(cl.unwrap()), Rc::clone(&current_node));
        };

        let properties = node.children().filter(|it| it.tag_name().name() == "property");
        for property in properties {
            let role = property.attributes().find(|a| a.name() == "role").unwrap().value();
            let value = property.attributes().find(|a| a.name() == "value").unwrap().value();
            let index_2_properties = model_builder_cache.index_2_property.borrow();
            let prop = index_2_properties.get(role).unwrap();
            current_node.add_property(prop, value.to_string());
        };

        let refs = node.children().filter(|it| it.tag_name().name() == "ref");
        for ref_ in refs {
            let role = ref_.attributes().find(|a| a.name() == "role").unwrap().value();
            let to = ref_.attributes().find(|a| a.name() == "to");
            let to: &str = if let Some(t) = to { 
                t.value() 
            } else {
                ref_.attributes().find(|a| a.name() == "node").unwrap().value()
            };
            let resolve = if let Some(r) = ref_.attributes().find(|a| a.name() == "resolve") {
                Some(String::from(r.value()))
            } else {
                None
            };

            let index_2_reference_links = model_builder_cache.index_2_reference_link.borrow();
            let reference_link = index_2_reference_links.get(&role.to_string()).unwrap();
            current_node.add_reference(reference_link, to.to_string(), resolve);
        };

        let nodes = node.children().filter(|it| it.tag_name().name() == "node");
        for node in nodes {
            Self::parse_node(&mut Some(Rc::clone(&current_node)), &node, language_builder, model_builder_cache);
        };

        Rc::clone(&current_node)
    }


}

#[cfg(test)]
mod tests {
    use std::path::PathBuf;

    use crate::builder::slanguage_builder::SLanguageBuilder;
    use crate::builder::smodel_builder_file_per_root_persistency::{SModelBuilderCache, SModelBuilderFilePerRootPersistency};
    use crate::builder::test_helper::{get_path_to_model_mpsr_example_lib_file, get_path_to_mpsr_example_lib_file};
    use crate::builder::test_helper::get_path_to_example_mpsr_model_files;

    #[test]
    fn test_model_extract_core_info() {
        let opt = roxmltree::ParsingOptions {
            allow_dtd: true,
            ..roxmltree::ParsingOptions::default()
        };

        // given
        let path_to_model_file = PathBuf::from(get_path_to_model_mpsr_example_lib_file());

        //when
        let model = SModelBuilderFilePerRootPersistency::extract_model_core_info(path_to_model_file, &opt);

        //assert
        assert_eq!(model.name, "mps.cli.lanuse.library_top.library_top");
        assert_eq!(model.uuid, "r:a96b23f6-56db-490c-a218-d40d11be7f1e");
        assert_eq!(model.path_to_model_file, get_path_to_model_mpsr_example_lib_file());
        assert_eq!(model.is_do_not_generate, true);
        assert!(model.is_file_per_root_persistency);
    }

    #[test]
    fn test_build_model() {
        // given
        let path_to_mpsr_file = PathBuf::from(get_path_to_example_mpsr_model_files());

        //when
        let mut language_builder = SLanguageBuilder::new();
        let mut model_builder_cache = SModelBuilderCache::new();
        SModelBuilderFilePerRootPersistency::build_model(path_to_mpsr_file, &mut language_builder, &model_builder_cache);

        //assert
        let index_2_imported_model_uuid = model_builder_cache.index_2_imported_model_uuid.borrow();
        assert_eq!(index_2_imported_model_uuid.len(), 1);
        assert!(index_2_imported_model_uuid.contains_key(&"q0v6".to_string()));
        let imported_model_uuid = index_2_imported_model_uuid.get(&"q0v6".to_string()).unwrap();
        assert_eq!(**imported_model_uuid, "r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed".to_string());
    }
}
