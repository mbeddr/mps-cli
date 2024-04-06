
class SRepository:

    def __init__(self):
        self.solutions = []
        self.languages = []
        self.model_2_uuid = {}

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

    def get_concepts(self):
        res = []
        for lan in self.languages:
            res.extend(lan.concepts)
        return res

    def get_nodes(self):
        res = []
        for sol in self.solutions:
            for mod in sol.models:
                res.extend(mod.get_nodes())
        return res

    def get_nodes_of_concept(self, concept_name):
        res = []
        for node in self.get_nodes():
            if node.concept.name == concept_name:
                res.append(node)
        return res

    def get_model_by_uuid(self, uuid):
        if len(self.model_2_uuid) == 0:
            for sol in self.solutions:
                for m in sol.models:
                    self.model_2_uuid[m.uuid] = m
        return self.model_2_uuid.get(uuid)
