use crate::model::slanguage::SLanguage;
use crate::model::smodel::SModel;
use crate::model::ssolution::SSolution;
use std::rc::Rc;
use std::cell::RefCell;

pub struct SRepository {
    pub solutions: Vec<SSolution>,
    pub languages: Vec<SLanguage>,
}

impl SRepository {
    pub fn new(solutions: Vec<SSolution>, languages: Vec<SLanguage>) -> Self {
        SRepository {
            solutions : solutions,
            languages : languages,
        }
    }

    #[allow(dead_code)]
    pub fn find_solution_by_name(&self, name: &str) -> Option<&SSolution> {        
        self.solutions.iter().find(|&ssolution| ssolution.name.eq(name))
    }

    #[allow(dead_code)]
    pub fn find_model_by_name(&self, name: &str) -> Option<Rc<RefCell<SModel>>> {        
        for s in self.solutions.iter() {
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
        for s in self.solutions.iter() {
            for m in s.models.iter() {
                res.push(Rc::clone(m));
            }
        }
        res
    }

    #[allow(dead_code)]
    pub fn get_model_by_uuid(&self, uuid: &str) -> Option<Rc<RefCell<SModel>>> {                
        for sol in self.solutions.iter() {
            for m in sol.models.iter() {
                if (**m).borrow().uuid.eq(uuid) {
                    return Some(Rc::clone(m));
                }
            }            
        }
        None
    }    
}