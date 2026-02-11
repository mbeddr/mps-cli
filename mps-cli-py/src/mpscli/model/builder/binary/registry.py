# mpscli/model/builder/binary/registry.py

from mpscli.model.builder.binary.utils import read_uuid, read_string
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder


def load_registry(reader, builder):
    language_count = reader.read_u16()

    concept_index = 0
    property_index = 0
    reference_index = 0
    child_index = 0

    for _ in range(language_count):
        language_id = read_uuid(reader)
        language_name = read_string(reader)

        language = SLanguageBuilder.get_language(language_name, language_id)

        concept_count = reader.read_u16()

        for _ in range(concept_count):
            concept_id = str(reader.read_u64())
            concept_name = read_string(reader)

            reader.read_u8()
            reader.read_u8()

            full_name = f"{language_name}.structure.{concept_name}"
            concept = SLanguageBuilder.get_concept(language, full_name, concept_id)

            builder.index_2_concept[str(concept_index)] = concept
            concept_index += 1

            property_count = reader.read_u16()
            for _ in range(property_count):
                prop_id = str(reader.read_u64())
                prop_name = read_string(reader)

                prop = SLanguageBuilder.get_property(concept, prop_name)
                builder.index_2_property[str(property_index)] = prop
                property_index += 1

            reference_count = reader.read_u16()
            for _ in range(reference_count):
                ref_id = str(reader.read_u64())
                ref_name = read_string(reader)

                ref = SLanguageBuilder.get_reference(concept, ref_name)
                builder.index_2_reference_role[str(reference_index)] = ref
                reference_index += 1

            containment_count = reader.read_u16()
            for _ in range(containment_count):
                link_id = str(reader.read_u64())
                link_name = read_string(reader)
                reader.read_u8()

                child = SLanguageBuilder.get_child(concept, link_name)
                builder.index_2_child_role_in_parent[str(child_index)] = child
                child_index += 1
