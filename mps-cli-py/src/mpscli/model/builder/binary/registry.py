from mpscli.model.builder.binary.model_input_stream import ModelInputStream
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder


def load_registry(reader: ModelInputStream, builder) -> None:
    REGISTRY_START = ModelInputStream.REGISTRY_START
    REGISTRY_END = ModelInputStream.REGISTRY_END
    # 0x12
    STUB_NONE = ModelInputStream.STUB_NONE
    # 0x13
    STUB_ID = ModelInputStream.STUB_ID

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
        # SLanguageId.getIdValue() = UUID
        language_uuid = reader.read_uuid()
        language_name = reader.read_string()
        language = SLanguageBuilder.get_language(language_name, language_uuid)

        concept_count = reader.read_u16()

        for _ in range(concept_count):
            # concept id is written as writeLong(ci.getConceptId().getIdValue())
            concept_id_raw = reader.read_u64()
            concept_id = str(concept_id_raw)

            short_name = reader.read_string()
            full_name = f"{language_name}.structure.{short_name}"

            flags = reader.read_u8()

            stub_token = reader.read_u8()
            if stub_token == STUB_NONE:
                # no stub
                pass
            elif stub_token == STUB_ID:
                # discard stub concept id
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
                reader.read_u64()  # property id
                name = reader.read_string()
                prop = SLanguageBuilder.get_property(concept, name)
                builder.index_2_property[property_index] = prop
                property_index += 1

            # associations (reference links)
            assoc_count = reader.read_u16()
            for _ in range(assoc_count):
                # association id
                reader.read_u64()
                name = reader.read_string()
                ref = SLanguageBuilder.get_reference(concept, name)
                builder.index_2_reference_role[reference_index] = ref
                reference_index += 1

            # aggregations (containment links/children)
            agg_count = reader.read_u16()
            for _ in range(agg_count):
                # aggregation id
                reader.read_u64()
                name = reader.read_string()
                # unordered flag
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
