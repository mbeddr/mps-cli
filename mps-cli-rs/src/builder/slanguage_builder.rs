use std::collections::HashMap;
use std::sync::Mutex;

use crate::model::sconcept::SConcept;
use crate::model::slanguage::SLanguage;

pub(crate) static SLANGUAGE_BUILDER: Mutex<SLanguageBuilder> = Mutex::new(SLanguageBuilder::new());

pub(crate) struct SLanguageBuilder {
    language_id_to_slanguage: Option<HashMap<String, SLanguage>>,
}

impl<'a> SLanguageBuilder {
    pub(crate) const fn new() -> Self {
        SLanguageBuilder {
            language_id_to_slanguage: None,
        }
    }

    fn ensure_initialized(&mut self) -> &mut HashMap<String, SLanguage> {
        self.language_id_to_slanguage.get_or_insert(HashMap::new())
    }

    pub(crate) fn get_or_build_language(&mut self, language_id: &String, language_name: &String) -> &mut SLanguage {
        let language_id_to_slanguage = self.ensure_initialized();
        language_id_to_slanguage.entry(language_id.to_string()).or_insert(SLanguage::new(language_name.to_string(), language_id.to_string()));
        language_id_to_slanguage.get_mut(language_id).unwrap()
    }

    pub(crate) fn get_or_create_concept_in_language(&mut self, language_id: &String, language_name: &String, concept_id: String, concept_name: String) -> &SConcept {
        self.ensure_initialized();
        let language: &mut SLanguage = self.get_or_build_language(language_id, language_name);
        if language.find_concept_by_name(&concept_name).is_none() {
            language.add_concept(SConcept::new(&concept_name, concept_id));
        }
        return language.find_concept_by_name(&concept_name).unwrap();
    }
}





