
from mpscli.model.SLanguage import SLanguage
from mpscli.model.SConcept import SConcept

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

    @classmethod
    def get_property(cls, concept, property_name):
        node_property = next((p for p in concept.properties if p == property_name), None)
        if node_property is None:
            concept.properties.append(property_name)
            node_property = property_name
        return node_property

    @classmethod
    def get_child(cls, concept, child_name):
        child_role = next((c for c in concept.children if c == child_name), None)
        if child_role is None:
            concept.children.append(child_name)
            child_role = child_name
        return child_role

    @classmethod
    def get_reference(cls, concept, reference_name):
        reference_role = next((r for r in concept.references if r == reference_name), None)
        if reference_role is None:
            concept.references.append(reference_name)
            reference_role = reference_name
        return reference_role