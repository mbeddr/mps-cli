import warnings
import xml.etree.ElementTree as ET
from pathlib import Path
from threading import Lock

from mpscli.model.SLanguage import SLanguage
from mpscli.model.SConcept import SConcept


class SLanguageBuilder:
    languages = {}
    # protectss languages dict, per-language _concepts_by_name dicts and per-concept properties/children/references
    # lists also.. needed because all get_ methods are called from multiple threads during parallel
    # parsing (phase3 ProcessPool workers and phase4 ProcessPool workerss)
    _lock = Lock()

    @classmethod
    def get_language(cls, name, uuid):
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
        # always acquire lock since _concepts_by_name is mutated here and by other threads..
        # SLanguage.__init__ always initialises _concepts_by_name so no hasattr check needed
        with cls._lock:
            concept = language._concepts_by_name.get(concept_name)
            if concept is None:
                concept = SConcept(concept_name, concept_uuid)
                language.concepts.append(concept)
                language._concepts_by_name[concept_name] = concept
        return concept

    @classmethod
    def get_property(cls, concept, property_name):
        # fast path cuz list iteration is GIL-atomic for reads in CPython
        node_property = next(
            (p for p in concept.properties if p == property_name), None
        )
        if node_property is not None:
            return node_property
        with cls._lock:
            # double-check inside lock since another thread may have added it
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
        if child_role is not None:
            return child_role
        with cls._lock:
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
        if reference_role is not None:
            return reference_role
        with cls._lock:
            reference_role = next(
                (r for r in concept.references if r == reference_name), None
            )
            if reference_role is None:
                concept.references.append(reference_name)
                reference_role = reference_name
        return reference_role

    @classmethod
    def load_from_mpl(cls, mpl_path: Path) -> SLanguage:
        # reads a .mpl file and enriches the matching SLanguage with its version
        # number and aspect models. if the language was already registered via
        # a registry section in a .mpb file, get_language() returns the same object
        # so no duplicate entries are created.
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
        # parse every .mpb in the models directory next to the .mpl file
        # these are the language aspects which is structure,, behavior, editor, constraints, typesystem, etc..
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
