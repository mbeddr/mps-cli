from mpscli.model.builder.binary.model_input_stream import ModelInputStream
from mpscli.model.builder.binary.constants import (
    REGISTRY_START,
    REGISTRY_END,
    STUB_NONE,
    STUB_ID,
)
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder


def load_registry(reader: ModelInputStream, builder) -> None:
    # mirrors BinaryPersistence.loadRegistry() in:
    # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BinaryPersistence.java
    #
    # Purpose: Reads the REGISTRY_START to REGISTRY_END section and builds four index maps from sequential
    # write-position integers to concept/property/reference/child objects and thesee indices are used throughout the
    # node tree so that each node only needs to write a small u16 index rather than repeating full concept and property
    # names on every node.
    #
    # Java uses four parallel int counters (conceptIndex, propertyIndex, associationIndex, aggregationIndex) that
    # increment as each entry is written and on read the same counterss are used to reconstruct the index and
    # Python mirrors this exactly with four local counters..
    #
    # Java builds live SConcept/SProperty/SReferenceLink/SContainmentLink objects via MetaAdapterFactory and
    # stores them in TIntObjectHashMap<T> (Trove, O(1) int keyed).
    # Python builds lightweight name/id wrapper objects via SLanguageBuilder and stores them in plain dicts which
    # is semantically identical and sufficient for CLI extraction.
    #
    # Per-language binary layout explained below (same in V2 and V3) -
    #   u16  lang_count
    #   per language:
    #    2xu64 SLanguageId UUID - (Java: os.writeUUID(ul.getLanguageId().getIdValue()))
    #    string language name
    #    u16 concept_count
    #    per concept:
    #       u64 concept id - (Java: os.writeLong(ci.getConceptId().getIdValue()))
    #       string short name - (Java: os.writeString(ci.getBriefName()))
    #       u8 flags byte - (ConceptKind<<4 | StaticScope | 0x80 if interface)
    #       u8 stub token - STUB_NONE(0x12) or STUB_ID(0x13)
    #       [u64 stub concept id] - only if stub token == STUB_ID
    #       u16 property_count - per prop:  u64 id + string name
    #       u16 association_count - per assoc: u64 id + string name
    #       u16 aggregation_count - per agg: u64 id + string name + bool unordered

    token = reader.read_u32()
    if token != REGISTRY_START:
        raise RuntimeError(
            f"Expected REGISTRY_START (0x{REGISTRY_START:08X}), "
            f"got 0x{token:08X} at pos {reader.tell() - 4}"
        )
    concept_index = 0
    property_index = 0
    reference_index = 0
    child_index = 0

    lang_count = reader.read_u16()
    for lang_i in range(lang_count):
        # SLanguageId.getIdValue() = UUID written as 2xu64
        language_uuid = reader.read_uuid()
        language_name = reader.read_string()
        language = SLanguageBuilder.get_language(language_name, language_uuid)

        concept_count = reader.read_u16()

        for _ in range(concept_count):
            # concept id written as writeLong(ci.getConceptId().getIdValue())
            concept_id_raw = reader.read_u64()
            concept_id = str(concept_id_raw)

            short_name = reader.read_string()
            # Java reconstructs the fqn via NameUtil.conceptFQNameFromNamespaceAndShortName(langName, shortName)
            # which produces "langName.structure.shortName" amd we replicate that here..
            full_name = f"{language_name}.structure.{short_name}"

            flags = reader.read_u8()

            stub_token = reader.read_u8()
            if stub_token == STUB_NONE:
                pass
            elif stub_token == STUB_ID:
                reader.read_u64()
            else:
                raise RuntimeError(
                    f"Unknown stub token 0x{stub_token:02X} "
                    f"for concept '{short_name}' at pos {reader.tell() - 1}"
                )

            concept = SLanguageBuilder.get_concept(language, full_name, concept_id)
            builder.index_2_concept[concept_index] = concept
            builder.concept_id_2_concept[concept_id] = concept
            concept_index += 1

            # properties
            prop_count = reader.read_u16()
            for _ in range(prop_count):
                reader.read_u64()  # property id (discarded - we use name only)
                name = reader.read_string()
                prop = SLanguageBuilder.get_property(concept, name)
                builder.index_2_property[property_index] = prop
                property_index += 1

            # associations (reference links)
            assoc_count = reader.read_u16()
            for _ in range(assoc_count):
                reader.read_u64()  # association id (discarded - we use name only)
                name = reader.read_string()
                ref = SLanguageBuilder.get_reference(concept, name)
                builder.index_2_reference_role[reference_index] = ref
                reference_index += 1

            # aggregations (containment links/child roles)
            agg_count = reader.read_u16()
            for _ in range(agg_count):
                reader.read_u64()
                name = reader.read_string()
                reader.read_bool()
                child = SLanguageBuilder.get_child(concept, name)
                builder.index_2_child_role_in_parent[child_index] = child
                child_index += 1

    token = reader.read_u32()
    if token != REGISTRY_END:
        raise RuntimeError(
            f"Expected REGISTRY_END (0x{REGISTRY_END:08X}), "
            f"got 0x{token:08X} at pos {reader.tell() - 4}"
        )
