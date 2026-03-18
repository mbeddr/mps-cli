from mpscli.model.builder.binary.model_input_stream import ModelInputStream
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder


def load_registry(reader: ModelInputStream, builder) -> None:
    """
    Parses the registry section of a .mpb file.

    Exact structure from BinaryPersistence.java saveRegistry() / loadRegistry():

        u32  REGISTRY_START
        u16  language_count
        for each language:
            uuid (2×u64)   language id
            string         language name
            u16            concept_count
            for each concept:
                u64        concept id (raw long, not uuid)
                string     concept short name
                u8         flags  (kind/scope/interface bits)
                u8         stub_token:
                               0x12 (STUB_NONE) → no stub
                               0x13 (STUB_ID)   → read u64 stub id
                u16        property_count
                for each property:
                    u64    property id
                    string property name
                u16        association_count
                for each association:
                    u64    association id
                    string association name
                u16        aggregation_count
                for each aggregation:
                    u64    aggregation id
                    string aggregation name
                    bool   unordered flag  (readBoolean = readByte != 0)
        u32  REGISTRY_END
    """

    REGISTRY_START = ModelInputStream.REGISTRY_START
    REGISTRY_END = ModelInputStream.REGISTRY_END
    STUB_NONE = ModelInputStream.STUB_NONE  # 0x12
    STUB_ID = ModelInputStream.STUB_ID  # 0x13

    token = reader.read_u32()
    if token != REGISTRY_START:
        raise RuntimeError(
            f"Expected REGISTRY_START (0x{REGISTRY_START:08X}), "
            f"got 0x{token:08X} at pos {reader.tell() - 4}"
        )

    print(f"[registry] REGISTRY_START confirmed at pos {reader.tell() - 4}")

    concept_index = 0
    property_index = 0
    reference_index = 0
    child_index = 0

    lang_count = reader.read_u16()
    print(f"[registry] language_count = {lang_count}")

    for lang_i in range(lang_count):
        language_uuid = reader.read_uuid()  # SLanguageId.getIdValue() = UUID
        language_name = reader.read_string()

        print(f"[registry]   LANG[{lang_i}]: {language_name!r}")

        language = SLanguageBuilder.get_language(language_name, language_uuid)

        concept_count = reader.read_u16()

        for _ in range(concept_count):
            # concept id is written as writeLong(ci.getConceptId().getIdValue())
            concept_id_raw = reader.read_u64()
            concept_id = str(concept_id_raw)

            short_name = reader.read_string()
            full_name = f"{language_name}.structure.{short_name}"

            flags = reader.read_u8()

            # CRITICAL: stub_token is ALWAYS written/read — it is NOT controlled by flags.
            stub_token = reader.read_u8()
            if stub_token == STUB_NONE:
                pass  # no stub
            elif stub_token == STUB_ID:
                reader.read_u64()  # stub concept id — discard
            else:
                raise RuntimeError(
                    f"Unknown stub token 0x{stub_token:02X} "
                    f"for concept '{short_name}' at pos {reader.tell() - 1}"
                )

            concept = SLanguageBuilder.get_concept(language, full_name, concept_id)
            builder.index_2_concept[concept_index] = concept
            builder.concept_id_2_concept[concept_id] = concept
            concept_index += 1

            # ── Properties ───────────────────────────────────────────────
            prop_count = reader.read_u16()
            for _ in range(prop_count):
                reader.read_u64()  # property id
                name = reader.read_string()
                prop = SLanguageBuilder.get_property(concept, name)
                builder.index_2_property[property_index] = prop
                property_index += 1

            # ── Associations (reference links) ────────────────────────────
            assoc_count = reader.read_u16()
            for _ in range(assoc_count):
                reader.read_u64()  # association id
                name = reader.read_string()
                ref = SLanguageBuilder.get_reference(concept, name)
                builder.index_2_reference_role[reference_index] = ref
                reference_index += 1

            # ── Aggregations (containment links / children) ───────────────
            agg_count = reader.read_u16()
            for _ in range(agg_count):
                reader.read_u64()  # aggregation id
                name = reader.read_string()
                reader.read_bool()  # unordered flag
                child = SLanguageBuilder.get_child(concept, name)
                builder.index_2_child_role_in_parent[child_index] = child
                child_index += 1

    token = reader.read_u32()
    if token != REGISTRY_END:
        raise RuntimeError(
            f"Expected REGISTRY_END (0x{REGISTRY_END:08X}), "
            f"got 0x{token:08X} at pos {reader.tell() - 4}"
        )

    print(f"[registry] REGISTRY_END confirmed at pos {reader.tell() - 4}")
    print(
        f"[registry] totals — concepts: {concept_index}, "
        f"properties: {property_index}, "
        f"references: {reference_index}, "
        f"children: {child_index}"
    )
