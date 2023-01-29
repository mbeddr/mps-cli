
class SRepository:

    def __init__(self):
        self.solutions = []
        self.languages = []

    def find_solution_by_name(self, name):
        for sol in self.solutions:
            if sol.name == name:
                return sol
        return None

    def find_model_by_name(self, name):
        for sol in self.solutions:
            for model in sol.models:
                if model.name == name:
                    return model
        return None

    def find_language_by_name(self, name):
        for lan in self.languages:
            if lan.name == name:
                return lan
        return None

    def find_concept_by_name(self, name):
        for lan in self.languages:
            for concept in lan.concepts:
                if concept.name == name:
                    return concept
        return None

    def get_nodes(self):
        res = []
        for sol in self.solutions:
            for mod in sol.models:
                res.extend(mod.get_nodes())
        return res

    def get_model_by_uuid(self, uuid):
        for sol in self.solutions:
            for m in sol.models:
                if m.uuid == uuid:
                    return m
        return None
