use std::collections::HashMap;
use std::fs::File;
use std::io::BufReader;
use std::path::PathBuf;
use std::sync::Mutex;

use quick_xml::events::Event;
use quick_xml::Reader;
use walkdir::{DirEntry, WalkDir};

use crate::builder::builder_helper::{convert_to_string, get_value_of_attribute_with_key, get_values_of_attributes_with_keys, panic_read_file, panic_unexpected_eof_read_file};
use crate::builder::slanguage_builder::SLANGUAGE_BUILDER;
use crate::model::sconcept::{SConcept, SProperty};
use crate::model::smodel::SModel;
use crate::model::snode::SNode;

static SMODEL_BUILDER_CACHE: Mutex<SModelBuilderCache> = Mutex::new(SModelBuilderCache::new());

pub struct SModelBuilderCache<'a> {
    pub index_2_concept: Option<HashMap<String, &'a SConcept>>,
    pub index_2_property: Option<HashMap<String, &'a SProperty>>,
    pub index_2_imported_model_uuid: Option<HashMap<String, String>>,
}

impl<'a> SModelBuilderCache<'a> {
    const fn new() -> Self {
        SModelBuilderCache {
            index_2_concept: None,
            index_2_property: None,
            index_2_imported_model_uuid: None,
        }
    }

    fn get_index_2_concept(&mut self) -> &mut HashMap<String, &'a SConcept> {
        self.index_2_concept.get_or_insert(HashMap::new())
    }

    fn get_index_2_property(&mut self) -> &mut HashMap<String, &'a SProperty> {
        self.index_2_property.get_or_insert(HashMap::new())
    }

    fn get_index_2_imported_model_uuid(&mut self) -> &mut HashMap<String, String> {
        self.index_2_imported_model_uuid.get_or_insert(HashMap::new())
    }
}

pub struct SModelBuilderFilePerRootPersistency {}

impl SModelBuilderFilePerRootPersistency {
    pub(crate) fn new() -> Self {
        SModelBuilderFilePerRootPersistency {}
    }
    pub(crate) fn build_model(&mut self, path_to_model: PathBuf) -> SModel {
        let mut model_file = path_to_model.clone();
        model_file.push(".model");
        let mut model: SModel = Self::extract_model_core_info(model_file);

        let mpsr_file_walker = WalkDir::new(path_to_model).min_depth(1).max_depth(1);
        let mpsr_files = mpsr_file_walker.into_iter().filter(|entry| {
            if entry.is_ok() {
                let dir_entry = entry.as_ref().unwrap();
                let extension = dir_entry.path().extension();
                return dir_entry.file_type().is_file() && extension.is_some_and(|e| e.eq("mpsr"));
            }
            return false;
        });
        mpsr_files.into_iter().for_each(|mpsr_file| {
            let root_node = self.build_root_node_from_file(mpsr_file.unwrap());
            model.root_nodes.push(root_node);
        });

        return model;
    }

    fn extract_model_core_info<'a>(path_to_model: PathBuf) -> SModel<'a> {
        let mut model_file_reader = Reader::from_file(path_to_model.clone()).unwrap();
        let mut name = String::new();
        let mut uuid = String::new();
        let mut is_do_not_generate = false;
        let mut buf = vec![];
        let mut model_found = false;
        let mut do_not_gen_found = false;
        while !(do_not_gen_found && model_found) {
            match model_file_reader.read_event_into(&mut buf) {
                Ok(Event::Start(ref e)) => {
                    match e.name().as_ref() {
                        b"model" => {
                            let value = get_value_of_attribute_with_key(e.attributes(), "ref").unwrap();
                            let index = value.find("(").unwrap();
                            uuid = value[..index].to_string();
                            name = value[index + 1..value.len() - 1].to_string();
                            model_found = true;
                        }
                        _ => {}
                    }
                }
                Ok(Event::Empty(ref e)) => {
                    if e.name().as_ref() == b"attribute" {
                        let attribute_name = get_value_of_attribute_with_key(e.attributes(), "name");
                        if attribute_name.is_some() && attribute_name.unwrap().eq("doNotGenerate") {
                            let value = get_value_of_attribute_with_key(e.attributes(), "value").unwrap();
                            is_do_not_generate = value.eq("true");
                            do_not_gen_found = true;
                        }
                    }
                }
                Ok(Event::Eof) => break,
                Err(e) => panic_read_file(&mut model_file_reader, e),
                _ => {}
            }
        }
        return SModel::new(name, uuid, convert_to_string(&path_to_model), is_do_not_generate, true);
    }

    fn build_root_node_from_file(&mut self, dir_entry: DirEntry) -> SNode {
        let mut mpsr_reader = Reader::from_file(dir_entry.path()).unwrap();
        let mut buf = vec![];
        let mut root_node = None;
        loop {
            match mpsr_reader.read_event_into(&mut buf) {
                Ok(Event::Start(ref e)) => match e.name().as_ref() {
                    b"imports" => self.parse_imports(&mut mpsr_reader),
                    b"registry" => self.parse_registry(&mut mpsr_reader),
                    b"node" => {
                        //root_node = Some(parse_node(&mpsr_reader, e, &mut buf))
                    }
                    _ => {}
                },
                Ok(Event::Eof) => break,
                Err(e) => panic_read_file(&mut mpsr_reader, e),
                _ => {}
            }
        }
        return root_node.unwrap();
    }

    fn parse_imports(&mut self, mpsr_reader: &mut Reader<BufReader<File>>) {
        let mut child_buf = vec![];
        loop {
            match mpsr_reader.read_event_into(&mut child_buf) {
                Ok(Event::Empty(e)) => {
                    let key_values = get_values_of_attributes_with_keys(e.attributes(), vec!["index", "ref"]);
                    if let Some(imported_model_ref) = key_values.get("ref") {
                        let index = imported_model_ref.find("(").unwrap();
                        let imported_model_uuid = imported_model_ref[..index].to_string();
                        if let Some(index_value) = key_values.get("index") {
                            SMODEL_BUILDER_CACHE.lock().unwrap().get_index_2_imported_model_uuid().insert(index_value.to_string(), imported_model_uuid);
                        }
                    }
                }
                Ok(Event::End(e)) => {
                    match e.name().as_ref() {
                        b"imports" => break,
                        _ => {}
                    }
                }
                Ok(Event::Eof) => panic_unexpected_eof_read_file(mpsr_reader),
                Err(e) => panic_read_file(mpsr_reader, e),
                _ => {}
            }
        }
    }

    fn parse_registry(&mut self, mpsr_reader: &mut Reader<BufReader<File>>) {
        let mut child_buf = vec![];
        loop {
            match mpsr_reader.read_event_into(&mut child_buf) {
                Ok(Event::Empty(e)) => {
                    match e.name().as_ref() {
                        b"language" => {
                            let id_name_attributes = get_values_of_attributes_with_keys(e.attributes(), vec!["id", "name"]);
                            let id = id_name_attributes.get("id").unwrap();
                            let name = id_name_attributes.get("name").unwrap();
                            self.parse_concept(mpsr_reader, id, name);
                        }

                        _ => {}
                    }
                }
                Ok(Event::End(e)) => {
                    match e.name().as_ref() {
                        b"registry" => break,
                        _ => {}
                    }
                }
                Ok(Event::Eof) => panic_unexpected_eof_read_file(mpsr_reader),
                Err(e) => panic_read_file(mpsr_reader, e),
                _ => {}
            }
        }
    }

    fn parse_concept(&mut self, mpsr_reader: &mut Reader<BufReader<File>>, language_id: &String, language_name: &String) {
        let mut concept_buf = vec![];

        loop {
            match mpsr_reader.read_event_into(&mut concept_buf) {
                Ok(Event::Empty(e)) => {
                    match e.name().as_ref() {
                        b"concept" => {
                            let mut id_map_index_map = get_values_of_attributes_with_keys(e.attributes(), vec!["id", "name", "index"]);
                            let concept_id = id_map_index_map.remove("id").unwrap();
                            let concept_name = id_map_index_map.remove("name").unwrap();
                            let mut language_builder = SLANGUAGE_BUILDER.lock().unwrap();
                            let concept: &SConcept = language_builder.get_or_create_concept_in_language(language_id, language_name, concept_id, concept_name);
                            SMODEL_BUILDER_CACHE.lock().unwrap().get_index_2_concept().insert(id_map_index_map.remove("index").unwrap(), concept);
                        }

                        _ => {}
                    }
                }
                Ok(Event::End(e)) => {
                    match e.name().as_ref() {
                        b"concept" => break,
                        _ => {}
                    }
                }
                Ok(Event::Eof) => panic_unexpected_eof_read_file(mpsr_reader),
                Err(e) => panic_read_file(mpsr_reader, e),
                _ => {}
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use std::path::PathBuf;

    use crate::builder::smodel_builder_file_per_root_persistency::{SMODEL_BUILDER_CACHE, SModelBuilderFilePerRootPersistency};
    use crate::builder::test_helper::{get_path_to_model_mpsr_example_lib_file, get_path_to_mpsr_example_lib_file};
    use crate::builder::test_helper::get_path_to_example_mpsr_model_files;

    #[test]
    fn test_model_extract_core_info() {
        // given
        let path_to_model_file = PathBuf::from(get_path_to_mpsr_example_lib_file());

        //when
        let model = SModelBuilderFilePerRootPersistency::extract_model_core_info(path_to_model_file);

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
        let mut smodel_builder = SModelBuilderFilePerRootPersistency::new();
        smodel_builder.build_model(path_to_mpsr_file);

        //assert
        assert_eq!(SMODEL_BUILDER_CACHE.lock().unwrap().get_index_2_imported_model_uuid().len(), 1);
        assert!(SMODEL_BUILDER_CACHE.lock().unwrap().get_index_2_imported_model_uuid().contains_key(&"q0v6".to_string()));
        let mut binding = SMODEL_BUILDER_CACHE.lock().unwrap();
        let imported_model_uuid = binding.get_index_2_imported_model_uuid().get(&"q0v6".to_string()).unwrap();
        assert_eq!(**imported_model_uuid, "ec5f093b-9d83-43a1-9b41-b5952da8b1ed".to_string());
    }
}
