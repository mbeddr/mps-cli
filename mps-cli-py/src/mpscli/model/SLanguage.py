class SLanguage:

    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid
        self.concepts = []

        # version number from the languageVersion attribute in the .mpl file..
        # stays 0 if this language was only seen via registry (never had its .mpl read)
        self.language_version = 0

        # aspect models loaded from the language's model's directory.
        # (behavior.mpb, structure.mpb, editor.mpb, constraints.mpb, etc..)
        # empty if the language's .mpl file was never found during scanning
        self.models = []

    def find_concept_by_name(self, name):
        for c in self.concepts:
            if c.name == name:
                return c
        return None

    def find_model_by_name(self, suffix):
        # find a specific aspect model by the last segment of its name.
        # example find_model_by_name("structure") matches "jetbrains.mps.lang.core.structure"
        for m in self.models:
            if m.name and m.name.endswith(suffix):
                return m
        return None
