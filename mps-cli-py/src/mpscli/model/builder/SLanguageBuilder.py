import warnings
import xml.etree.ElementTree as ET
from pathlib import Path
from threading import Lock

from mpscli.model.SLanguage import SLanguage
from mpscli.model.SConcept import SConcept


class SLanguageBuilder:
    languages = {}
    # protects languages dict and per-language _concepts_by_name dicts..
    # needed because get_concept is called from multiple threads during warm cache loads so..
    _lock = Lock()

    @classmethod
    def get_language(cls, name, uuid):
        # dict reads are GIL atomic I think so no lock needed on the fast path
        lan = cls.languages.get(name)
        if lan is not None:
            return lan
        with cls._lock:
            lan = cls.languages.get(name)
            if lan is None:
                lan = SLanguage(name, uuid)
                cls.languages[name] = lan
        return lan

    @classmethod
    def get_concept(cls, language, concept_name, concept_uuid):
        if not hasattr(language, "_concepts_by_name"):
            language._concepts_by_name = {c.name: c for c in language.concepts}
        concept = language._concepts_by_name.get(concept_name)
        if concept is not None:
            return concept
        with cls._lock:
            concept = language._concepts_by_name.get(concept_name)
            if concept is None:
                concept = SConcept(concept_name, concept_uuid)
                language.concepts.append(concept)
                language._concepts_by_name[concept_name] = concept
        return concept

    @classmethod
    def get_property(cls, concept, property_name):
        node_property = next(
            (p for p in concept.properties if p == property_name), None
        )
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
        reference_role = next(
            (r for r in concept.references if r == reference_name), None
        )
        if reference_role is None:
            concept.references.append(reference_name)
            reference_role = reference_name
        return reference_role

    @classmethod
    def load_from_mpl(cls, mpl_path: Path) -> SLanguage:
        # reads a .mpl file and improves the matching SLanguage with its version number and aspect models..
        # If the language was already registered via a registry section in a .mpb file, get_language() returns
        # the same object so no duplicate entries are created I guess..
        try:
            return cls._read_and_enrich(mpl_path)
        except Exception as exc:
            warnings.warn(f"Failed to read language from {mpl_path.name}: {exc}")
            return None

    @classmethod
    def _read_and_enrich(cls, mpl_path: Path) -> SLanguage:
        root = ET.parse(mpl_path).getroot()
        namespace = root.get("namespace", "")
        uuid = root.get("uuid", "")
        version = int(root.get("languageVersion", "0"))
        lang = cls.get_language(namespace, uuid)
        lang.language_version = version
        lang.models = cls._load_aspect_models(mpl_path.parent / "models")
        return lang

    @classmethod
    def _load_aspect_models(cls, models_dir: Path) -> list:
        # parses every .mpb in the models directory next to the .mpl file.
        # these are the language aspect models such as the structure, behavior, editor, constraints, typesystem etc.
        # import is kept local to avoid pulling SModelBuilderBinaryPersistency and all its binary parsing
        # dependencies into the module at load time..
        if not models_dir.exists():
            return []
        from mpscli.model.builder.SModelBuilderBinaryPersistency import (
            SModelBuilderBinaryPersistency,
        )

        loaded = []
        for mpb_file in sorted(models_dir.glob("*.mpb")):
            try:
                model = SModelBuilderBinaryPersistency().build(str(mpb_file))
                if model is not None:
                    loaded.append(model)
            except Exception as exc:
                warnings.warn(f"Failed to parse aspect model {mpb_file.name}: {exc}")
        return loaded
