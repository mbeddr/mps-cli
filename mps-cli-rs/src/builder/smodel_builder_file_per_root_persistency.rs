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
    pub index_2_concept: HashMap<String, Rc<SConcept>>,
    pub index_2_property: HashMap<String, Rc<SProperty>>,
    pub index_2_containment_link: HashMap<String, Rc<SContainmentLink>>,
    pub index_2_reference_link: HashMap<String, Rc<SReferenceLink>>,
    pub index_2_imported_model_uuid: HashMap<String, String>,
    pub index_2_model : HashMap<String, Rc<RefCell<SModel>>>,
    pub current_model : Option<Rc<RefCell<SModel>>>,
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
            current_model : None,
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

pub struct SModelBuilderFilePerRootPersistency {}

impl SModelBuilderFilePerRootPersistency {
    
    pub(crate) fn build_model<'a>(path_to_model: PathBuf, language_builder : &mut SLanguageBuilder, model_builder_cache : &mut SModelBuilderCache) -> Rc<RefCell<SModel>> {
        let mut model_file = path_to_model.clone();
        model_file.push(".model");
        let model: Rc<RefCell<SModel>> = Self::extract_model_core_info(model_file, model_builder_cache);
        model_builder_cache.current_model = Some(Rc::clone(&model));

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

    fn extract_model_core_info<'a>(path_to_model: PathBuf, model_builder_cache : &mut SModelBuilderCache) -> Rc<RefCell<SModel>> {
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

    fn build_root_node_from_file<'a>(dir_entry: DirEntry, language_builder : &mut SLanguageBuilder, model_builder_cache : &mut SModelBuilderCache) -> Option<Rc<SNode>> {        
        let file = std::fs::File::open(dir_entry.path().as_os_str());  

        let mut s = String::new();
        let _ = file.unwrap().read_to_string(&mut s);
        let parse_res = roxmltree::Document::parse(&s);
          
        let document = parse_res.unwrap();
        Self::parse_imports(&document, model_builder_cache);
        Self::parse_registry(&document, language_builder, model_builder_cache);
        
        let node = document.root_element().children().find(|it| it.tag_name().name() == "node");
        let mut parent: Option<Rc<SNode>> = None;
        Some(Self::parse_node(&mut parent, &node.unwrap(), language_builder, model_builder_cache))    
    }

    fn parse_imports(document: &Document, model_builder_cache : &mut SModelBuilderCache) {
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
                        model_builder_cache.index_2_imported_model_uuid.insert(index.to_string(), uuid);
                    }
                }
            },
            _ => ()
        }
    }

    fn parse_registry<'a>(document: &Document, language_builder : &mut SLanguageBuilder, model_builder_cache : &mut SModelBuilderCache) {                
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


    fn parse_node<'a>(parent_node : &mut Option<Rc<SNode>>, node: &Node, language_builder : &SLanguageBuilder, model_builder_cache : &mut SModelBuilderCache) -> Rc<SNode> {
        let node_attrs = node.attributes();
        let concept_index = (node_attrs.clone()).into_iter().find(|a| a.name() == "concept").unwrap().value();
        let node_id = (node_attrs.clone()).into_iter().find(|a| a.name() == "id").unwrap().value();
        let role = (node_attrs.clone()).into_iter().find(|a| a.name() == "role");
        let role = if role.is_none() { None } else { Some(role.unwrap().value().to_string()) };

        let index_2_concept = &model_builder_cache.index_2_concept;
        
        let my_concept = index_2_concept.get(concept_index).unwrap();
        let role_human_readable = match role.clone() {
            Some(role_string) => {
                let index_2_containment_link = &model_builder_cache.index_2_containment_link;
                let r = index_2_containment_link.get(&role_string).unwrap();
                Some(String::from(&r.name))
            },
            None => None,
        };
        let mut current_node = SNode::new(node_id.to_string(), Rc::clone(my_concept), role_human_readable);
        
        let properties = node.children().filter(|it| it.tag_name().name() == "property");
        for property in properties {
            let role = property.attributes().find(|a| a.name() == "role").unwrap().value();
            let value = property.attributes().find(|a| a.name() == "value").unwrap().value();
            let index_2_properties = &model_builder_cache.index_2_property;
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

            let index_2_reference_links = &model_builder_cache.index_2_reference_link;
            let reference_link = index_2_reference_links.get(&role.to_string()).unwrap();
            
            let model_id : String;
            let node_id  : String;
            if let Some(index) = to.find(":") {
                let model_index = &to[0..index];
                let mm = &model_builder_cache.index_2_imported_model_uuid;
                model_id = String::from(mm.get(model_index).unwrap());
                node_id = String::from(&to[index + 1..to.len()]);
            } else {
                let crt_model = &model_builder_cache.current_model;
                let m = crt_model.as_ref().unwrap();
                let m = m.as_ref().borrow();
                model_id = String::from(m.uuid.as_str());
                node_id = String::from(to);
            };

            current_node.add_reference(reference_link, model_id, node_id, resolve);
        };

        let current_node_rc : Rc<SNode>;

        if let Some(parent) = parent_node {
            let index_2_containment_link = &model_builder_cache.index_2_containment_link;
            let cl = index_2_containment_link.get(&role.unwrap());
            current_node.set_parent(Rc::clone(parent));
            current_node_rc = Rc::new(current_node);
            parent.borrow_mut().add_child(Rc::clone(cl.unwrap()), Rc::clone(&current_node_rc));
        } else {
            current_node_rc = Rc::new(current_node);
        };

        let nodes = node.children().filter(|it| it.tag_name().name() == "node");
        for node in nodes {
            Self::parse_node(&mut Some(Rc::clone(&current_node_rc)), &node, language_builder, model_builder_cache);
        };


        Rc::clone(&current_node_rc)
    }


}

#[cfg(test)]
mod tests {
    use std::cell::RefCell;
    use std::path::PathBuf;

    use crate::builder::smodel_builder_file_per_root_persistency::{SModelBuilderCache, SModelBuilderFilePerRootPersistency};

    #[test]
    fn test_model_extract_core_info() {
        // given
        let path = "../mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.library_top/.model"; 
        let path_to_model_file = PathBuf::from(path);

        //when
        let mut model_builder_cache = SModelBuilderCache::new();
        let temp = SModelBuilderFilePerRootPersistency::extract_model_core_info(path_to_model_file, &mut model_builder_cache);
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
