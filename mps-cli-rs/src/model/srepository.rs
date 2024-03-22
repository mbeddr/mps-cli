use std::collections::HashMap;

use uuid::Uuid;

use crate::model::slanguage::SLanguage;
use crate::model::smodel::SModel;
use crate::model::snode::SNode;
use crate::model::ssolution::SSolution;

pub struct SRepository<'a> {
    solutions: Vec<SSolution<'a>>,
    languages: Vec<SLanguage>,

    models: Vec<&'a SModel<'a>>,
    nodes: Vec<&'a SNode<'a>>,
    id_2_models_cache: HashMap<Uuid, &'a SModel<'a>>,
    id_2_nodes_cache: HashMap<Uuid, &'a SNode<'a>>,
}

impl<'a> SRepository<'a> {
    pub fn new(solutions: Vec<SSolution<'a>>, languages: Vec<SLanguage>) -> Self {
        SRepository {
            solutions,
            languages,
            models: vec![],
            nodes: vec![],
            id_2_models_cache: HashMap::new(),
            id_2_nodes_cache: HashMap::new(),
        }
    }

    fn find_solution_by_name(&self, name: &String) -> Option<&SSolution> {
        let found_solution = self.solutions.iter().find(|&ssolution| ssolution.name.eq(name));
        return found_solution;
    }

    pub fn get_model_by_uuid(&self, uuid: &Uuid) -> Option<&SModel> {
        None
    }

    fn find_model_by_name(&self, name: &String) -> Option<&SModel> {
        None
    }
}