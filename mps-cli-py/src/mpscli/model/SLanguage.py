
class SLanguage:

    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid
        self.concepts = []


    def find_concept_by_name(self, name):
        for c in self.concepts:
            if c.name == name:
                return c
        return None