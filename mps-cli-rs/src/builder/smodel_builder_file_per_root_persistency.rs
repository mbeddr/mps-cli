use std::borrow::BorrowMut;
use std::collections::HashMap;
use std::path::PathBuf;
use std::io::Read;
use roxmltree::{Document, Node};
use std::rc::Rc;
use std::cell::RefCell;

use walkdir::{DirEntry, WalkDir};

use crate::model::sconcept::{SConcept, SContainmentLink, SProperty, SReferenceLink};
use crate::model::smodel::SModel;
use crate::model::snode::SNode;
use super::slanguage_builder::SLanguageBuilder;


#[derive(Clone)]
pub struct SModelBuilderCache {
    pub index_2_concept: RefCell<HashMap<String, Rc<SConcept>>>,
    pub index_2_property: RefCell<HashMap<String, Rc<SProperty>>>,
    pub index_2_containment_link: RefCell<HashMap<String, Rc<SContainmentLink>>>,
    pub index_2_reference_link: RefCell<HashMap<String, Rc<SReferenceLink>>>,
    pub index_2_imported_model_uuid: RefCell<HashMap<String, String>>,
    pub index_2_model : RefCell<HashMap<String, Rc<RefCell<SModel>>>>,
}

impl SModelBuilderCache {
    pub fn new() -> Self {
        SModelBuilderCache {
            index_2_concept: RefCell::new(HashMap::new()),
            index_2_property: RefCell::new(HashMap::new()),
            index_2_containment_link : RefCell::new(HashMap::new()),
            index_2_reference_link : RefCell::new(HashMap::new()),
            index_2_imported_model_uuid: RefCell::new(HashMap::new()),
            index_2_model: RefCell::new(HashMap::new()),
        }
    }

    pub fn get_model(&self, name : String, uuid : String) -> Rc<RefCell<SModel>> {
        let mut i2m = self.index_2_model.borrow_mut();
        if let Some(model) = i2m.get(&uuid) { 
            Rc::clone(&model) 
        } else {
            let temp = Rc::new(RefCell::new(SModel::new(name.clone(), uuid.clone())));
            i2m.insert(uuid, temp.clone());
            temp.clone()  
        }
    }

}

pub struct SModelBuilderFilePerRootPersistency {}

impl SModelBuilderFilePerRootPersistency {
    
    pub(crate) fn build_model<'a>(path_to_model: PathBuf, language_builder : &RefCell<SLanguageBuilder>, model_builder_cache : &RefCell<SModelBuilderCache>) -> Rc<RefCell<SModel>> {
        let mut model_file = path_to_model.clone();
        model_file.push(".model");
        let model: Rc<RefCell<SModel>> = Self::extract_model_core_info(model_file, model_builder_cache);

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
            if let Some(r) = Self::build_root_node_from_file(file, language_builder, model_builder_cache) {
                roots.push(r);
            }
        };
        model.as_ref().borrow_mut().root_nodes.extend(roots);

        return model;
    }

    fn extract_model_core_info<'a>(path_to_model: PathBuf, model_builder_cache : &RefCell<SModelBuilderCache>) -> Rc<RefCell<SModel>> {
        let path_to_model_file = path_to_model.to_str().unwrap().to_string();        

        let file = std::fs::File::open(path_to_model_file.clone());  
        if file.is_err() {
            panic!("file not found '{}'", path_to_model_file);
        }
        let mut s = String::new();
        let _ = file.unwrap().read_to_string(&mut s);
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
        
        let model_builder_cache = model_builder_cache.borrow();
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

    fn build_root_node_from_file<'a>(dir_entry: DirEntry, language_builder : &RefCell<SLanguageBuilder>, model_builder_cache : &RefCell<SModelBuilderCache>) -> Option<Rc<SNode>> {        
        let file = std::fs::File::open(dir_entry.path().as_os_str());  

        let mut s = String::new();
        let _ = file.unwrap().read_to_string(&mut s);
        let parse_res = roxmltree::Document::parse(&s);
          
        let document = parse_res.unwrap();
        Self::parse_imports(&document, &model_builder_cache);
        Self::parse_registry(&document, &language_builder, &model_builder_cache);
        
        let node = document.root_element().children().find(|it| it.tag_name().name() == "node");
        let mut parent: Option<Rc<SNode>> = None;
        Some(Self::parse_node(&mut parent, &node.unwrap(), &(language_builder.borrow()), &(model_builder_cache.borrow())))    
    }

    fn parse_imports(document: &Document, model_builder_cache : &RefCell<SModelBuilderCache>) {
        let model_builder_cache = model_builder_cache.borrow();
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

    fn parse_registry<'a>(document: &Document, language_builder : &RefCell<SLanguageBuilder>, model_builder_cache : &RefCell<SModelBuilderCache>) {
        let language_builder = language_builder.borrow();
        let model_builder_cache = model_builder_cache.borrow();
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
                        let conc = language_builder.get_or_create_concept(Rc::clone(&lang), concept_id, concept_name);
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


    fn parse_node<'a>(parent_node : &mut Option<Rc<SNode>>, node: &Node, language_builder : &SLanguageBuilder, model_builder_cache : &SModelBuilderCache) -> Rc<SNode> {
        let node_attrs = node.attributes();
        let concept_index = (node_attrs.clone()).into_iter().find(|a| a.name() == "concept").unwrap().value();
        let node_id = (node_attrs.clone()).into_iter().find(|a| a.name() == "id").unwrap().value();
        let role = (node_attrs.clone()).into_iter().find(|a| a.name() == "role");
        let role = if role.is_none() { None } else { Some(role.unwrap().value().to_string()) };

        let index_2_concept = model_builder_cache.index_2_concept.borrow();
        
        let my_concept = index_2_concept.get(concept_index).unwrap();
        let role_human_readable = match role.clone() {
            Some(role_string) => {
                let index_2_containment_link = model_builder_cache.index_2_containment_link.borrow();
                let r = index_2_containment_link.get(&role_string).unwrap();
                Some(String::from(&r.name))
            },
            None => None,
        };
        let current_node : Rc<SNode> = Rc::new(SNode::new(node_id.to_string(), Rc::clone(my_concept), role_human_readable));
        
        if let Some(parent) = parent_node {
            let index_2_containment_link = model_builder_cache.index_2_containment_link.borrow();
            let cl = index_2_containment_link.get(&role.unwrap());
            parent.borrow_mut().add_child(Rc::clone(cl.unwrap()), Rc::clone(&current_node));
            current_node.set_parent(Rc::clone(parent));
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
    use std::cell::RefCell;
    use std::path::PathBuf;
    use std::rc::Rc;

    use crate::builder::slanguage_builder::SLanguageBuilder;
    use crate::builder::smodel_builder_file_per_root_persistency::{SModelBuilderCache, SModelBuilderFilePerRootPersistency};
    use crate::model::snode::SNode;

    #[test]
    fn test_model_extract_core_info() {
        // given
        let path = "../mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.library_top/.model"; 
        let path_to_model_file = PathBuf::from(path);

        //when
        let model_builder_cache = RefCell::new(SModelBuilderCache::new());
        let temp = SModelBuilderFilePerRootPersistency::extract_model_core_info(path_to_model_file, &model_builder_cache);
        let model = temp.borrow();

        //assert
        assert_eq!(model.name, "mps.cli.lanuse.library_top.library_top");
        assert_eq!(model.uuid, "r:a96b23f6-56db-490c-a218-d40d11be7f1e");
        assert_eq!(model.path_to_model_file, path);
        assert_eq!(model.is_do_not_generate, true);
        assert!(model.is_file_per_root_persistency);
        assert_eq!(model.imported_models.len(), 1);
        let import = model.imported_models.first().unwrap();
        assert_eq!(import.borrow_mut().name, "mps.cli.lanuse.library_top.authors_top");
        assert_eq!(import.borrow_mut().uuid, "r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed");
    }

}
