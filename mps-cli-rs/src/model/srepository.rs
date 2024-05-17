use std::collections::HashMap;

use crate::model::slanguage::SLanguage;
use crate::model::smodel::SModel;
use crate::model::snode::SNode;
use crate::model::ssolution::SSolution;
use std::rc::Rc;
use std::cell::RefCell;

pub struct SRepository<'a> {
    pub solutions: RefCell<Vec<Rc<SSolution<'a>>>>,
    languages: RefCell<Vec<Rc<SLanguage>>>,

    models: RefCell<Vec<Rc<SModel<'a>>>>,
    nodes: RefCell<Vec<Rc<SNode<'a>>>>,
}

impl<'a> SRepository<'a> {
    pub fn new(solutions: Vec<Rc<SSolution<'a>>>, languages: Vec<Rc<SLanguage>>) -> Self {
        SRepository {
            solutions : RefCell::new(solutions),
            languages : RefCell::new(languages),
            models: RefCell::new(vec![]),
            nodes: RefCell::new(vec![]),
        }
    }

    pub fn find_solution_by_name(&self, name: &String) -> Option<Rc<SSolution<'a>>> {
        let solutions = self.solutions.borrow();
        let found_solution = solutions.iter().find(|&ssolution| ssolution.name.eq(name));
        if let Some(found_solution) = found_solution {
            return Some(Rc::clone(found_solution));
        }
        None
    }

    pub fn get_model_by_uuid(&self, uuid: &'a String) -> Option<Rc<SModel<'a>>> {
        let models = self.models.borrow();
        let res = models.iter().find(|&model| model.uuid.eq(uuid));
        if let Some(res) = res {
            return Some(Rc::clone(res));
        }
        None
    }    
}