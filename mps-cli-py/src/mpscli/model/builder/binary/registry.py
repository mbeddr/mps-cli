# mpscli/model/builder/binary/registry.py

from mpscli.model.builder.binary.utils import read_uuid, read_string


def load_registry(reader, registry):
    language_count = reader.read_u16()

    concept_index = 0
    property_index = 0
    reference_index = 0
    containment_index = 0

    for _ in range(language_count):
        language_id = read_uuid(reader)
        language_name = read_string(reader)

        # --- concepts ---
        concept_count = reader.read_u16()
        for _ in range(concept_count):
            concept_id = reader.read_u64()
            concept_name = read_string(reader)

            flags = reader.read_u8()
            stub_token = reader.read_u8()

            registry["concepts"][str(concept_index)] = {
                "id": concept_id,
                "name": f"{language_name}.structure.{concept_name}"
            }
            concept_index += 1

            # --- properties ---
            property_count = reader.read_u16()
            for _ in range(property_count):
                prop_id = reader.read_u64()
                prop_name = read_string(reader)

                registry["properties"][str(property_index)] = {
                    "id": prop_id,
                    "name": prop_name
                }
                property_index += 1

            # --- references ---
            reference_count = reader.read_u16()
            for _ in range(reference_count):
                ref_id = reader.read_u64()
                ref_name = read_string(reader)

                registry["references"][str(reference_index)] = {
                    "id": ref_id,
                    "name": ref_name
                }
                reference_index += 1

            # --- containments ---
            containment_count = reader.read_u16()
            for _ in range(containment_count):
                link_id = reader.read_u64()
                link_name = read_string(reader)
                unordered = reader.read_u8() != 0

                registry["containments"][str(containment_index)] = {
                    "id": link_id,
                    "name": link_name,
                    "unordered": unordered
                }
                containment_index += 1
