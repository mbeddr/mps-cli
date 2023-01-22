
from model.SLanguage import SLanguage
from model.SConcept import SConcept

class SLanguageBuilder:
    languages = {}

    @classmethod
    def get_language(cls, name, uuid):
        lan = cls.languages.get(name, None)
        if lan is None:
            lan = SLanguage(name, uuid)
            cls.languages[name] = lan
        return lan

    @classmethod
    def get_concept(cls, language, concept_name, concept_uuid):
        concept = next((c for c in language.concepts if c.name == concept_name), None)
        if concept is None:
            concept = SConcept(concept_name, concept_uuid)
            language.concepts.append(concept)
        return concept


