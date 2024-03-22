use uuid::Uuid;

use crate::model::sconcept::SConcept;

pub struct SLanguage {
    name: String,
    uuid: Uuid,
    concepts: Vec<SConcept>,
}

impl SLanguage {
    pub fn new(name: String, uuid: Uuid) -> Self {
        SLanguage {
            name,
            uuid,
            concepts: vec![],
        }
    }

    pub fn find_concept_by_name(&self, concept_name: &str) -> Option<&SConcept> {
        self.concepts.iter().find(|&concept| concept.name.eq(concept_name))
    }
}

#[cfg(test)]
mod tests {
    use uuid::Uuid;

    use crate::model::sconcept::SConcept;
    use crate::model::slanguage::SLanguage;

    #[test]
    fn test_find_concept_by_name() {
        // given
        let mut slanguage = SLanguage::new("FirstLanguage".to_string(), Uuid::new_v4());
        let first_concept_name = "FirstConcept";
        let first_concept: SConcept = SConcept::new(first_concept_name.to_string(), Uuid::new_v4());
        let second_concept_name = "SecondConcept";
        let second_concept = SConcept::new(second_concept_name.to_string(), Uuid::new_v4());
        slanguage.concepts.push(first_concept);
        slanguage.concepts.push(second_concept);

        //when
        let found_first_concept = slanguage.find_concept_by_name(first_concept_name);
        let found_second_concept = slanguage.find_concept_by_name(second_concept_name);
        let non_found_concept = slanguage.find_concept_by_name("ThirdConcept");

        //assert
        assert_eq!(slanguage.concepts.len(), 2);
        assert_eq!(found_first_concept, slanguage.concepts.get(0), "First concept not found");
        assert_eq!(found_second_concept, slanguage.concepts.get(1), "Second concept not found");
        assert_eq!(non_found_concept, None);
    }
}