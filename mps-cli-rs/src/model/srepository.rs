use crate::model::slanguage::SLanguage;
use crate::model::smodel::SModel;
use crate::model::ssolution::SSolution;
use std::rc::Rc;
use std::cell::RefCell;

pub struct SRepository {
    pub solutions: RefCell<Vec<Rc<SSolution>>>,
    pub languages: RefCell<Vec<Rc<SLanguage>>>,
}

impl SRepository {
    pub fn new(solutions: Vec<Rc<SSolution>>, languages: Vec<Rc<SLanguage>>) -> Self {
        SRepository {
            solutions : RefCell::new(solutions),
            languages : RefCell::new(languages),
        }
    }

    #[allow(dead_code)]
    pub fn find_solution_by_name(&self, name: &str) -> Option<Rc<SSolution>> {
        let solutions = self.solutions.borrow();
        let found_solution = solutions.iter().find(|&ssolution| ssolution.name.eq(name));
        found_solution.map(|s| Rc::clone(s))
    }

    #[allow(dead_code)]
    pub fn find_model_by_name(&self, name: &str) -> Option<Rc<RefCell<SModel>>> {
        let solutions = self.solutions.borrow();
        for s in solutions.iter() {
            for m in s.models.iter() {
                if let Ok(model) = m.clone().try_borrow() { 
                    println!("model {}", model.name);
                    if model.name == name { return Some(Rc::clone(m)); }
                }
            }
        }
        None
    }

    #[allow(dead_code)]
    pub fn get_all_models(&self) -> Vec<Rc<RefCell<SModel>>> {
        let mut res : Vec<Rc<RefCell<SModel>>> = Vec::new();
        let solutions = self.solutions.borrow();
        for s in solutions.iter() {
            for m in s.models.iter() {
                res.push(Rc::clone(m));
            }
        }
        res
    }

    #[allow(dead_code)]
    pub fn get_model_by_uuid(&self, uuid: &str) -> Option<Rc<RefCell<SModel>>> {        
        let solutions = self.solutions.borrow();
        for sol in solutions.iter() {
            for m in sol.models.iter() {
                if (**m).borrow().uuid.eq(uuid) {
                    return Some(Rc::clone(m));
                }
            }            
        }
        None
    }    
}