use crate::model::slanguage::SLanguage;
use crate::model::smodel::SModel;
use crate::model::snode::SNode;
use crate::model::ssolution::SSolution;
use std::borrow::Borrow;
use std::ops::Deref;
use std::rc::Rc;
use std::cell::RefCell;

pub struct SRepository<'a> {
    pub solutions: RefCell<Vec<Rc<SSolution<'a>>>>,
    languages: RefCell<Vec<Rc<SLanguage>>>,
}

impl<'a> SRepository<'a> {
    pub fn new(solutions: Vec<Rc<SSolution<'a>>>, languages: Vec<Rc<SLanguage>>) -> Self {
        SRepository {
            solutions : RefCell::new(solutions),
            languages : RefCell::new(languages),
        }
    }

    pub fn find_solution_by_name(&self, name: &str) -> Option<Rc<SSolution<'a>>> {
        let solutions = self.solutions.borrow();
        let found_solution = solutions.iter().find(|&ssolution| ssolution.name.eq(name));
        if let Some(found_solution) = found_solution {
            return Some(Rc::clone(found_solution));
        }
        None
    }

    /*pub fn get_model_by_uuid(&self, uuid: &str) -> Option<Rc<RefCell<SModel<'a>>>> {        
        let solutions = self.solutions.borrow();
        for sol in solutions.into_iter() {
            let models = sol.models;
            for m in models.iter() {
                if (**m).borrow().uuid.eq(uuid) {
                    return Some(Rc::clone(m));
                }
            }            
        }
        None
    }*/    
}