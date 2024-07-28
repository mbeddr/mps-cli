use std::cell::RefCell;
use std::rc::Rc;

struct Person {
    name: String,
}

struct Company {
    employees: RefCell<Vec<Rc<Person>>>,
}

impl Company {
    fn search_employee(&self, name: &str) -> Option<Rc<Person>> {
        self.employees
            .borrow()
            .iter()
            .find(|employee| employee.name == name)
            .map(|employee| Rc::clone(employee))
    }
}
