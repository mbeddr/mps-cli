from .constants import *
from .utils import read_string, read_uuid


def read_children(reader, registry, imported_models, parent=None):
    child_count = reader.read_u32()

    nodes = []
    for _ in range(child_count):
        node = read_node(reader, registry, imported_models, parent)
        nodes.append(node)

    return nodes


def read_node(reader, registry, imported_models, parent=None):
    concept_index = reader.read_u16()
    concept = registry["concepts"][str(concept_index)]
    concept_name = concept["name"]

    node_id = read_node_id(reader)

    aggregation_index = reader.read_u16()

    open_curly = reader.read_u8()
    if chr(open_curly) != "{":
        raise ValueError("Invalid node start")

    properties_count = reader.read_u16()
    properties = {}

    for _ in range(properties_count):
        prop_index = reader.read_u16()
        prop = registry["properties"][str(prop_index)]
        prop_name = prop["name"]
        prop_value = read_string(reader)
        properties[prop_name] = prop_value

    user_objects_count = reader.read_u16()
    if user_objects_count != 0:
        raise ValueError("User objects not supported")

    references_count = reader.read_u16()
    references = []

    for _ in range(references_count):
        ref = read_reference(reader, imported_models)
        references.append(ref)

    node = {
        "id": node_id,
        "concept": concept_name,
        "properties": properties,
        "references": references,
        "children": [],
    }

    children = read_children(reader, registry, imported_models, parent=node)
    node["children"] = children

    closed_curly = reader.read_u8()
    if chr(closed_curly) != "}":
        raise ValueError("Invalid node end")

    return node


def read_node_id(reader):
    kind = reader.read_u8()

    if kind == NODEID_LONG:
        return str(reader.read_u64())

    if kind == NODEID_STRING:
        return read_string(reader)

    raise ValueError(f"Unknown node id kind: 0x{kind:X}")


def read_reference(reader, imported_models):
    reference_index = reader.read_u16()

    kind = reader.read_u8()
    if kind != 1:
        raise ValueError("Only direct references supported")

    target_node_id = read_node_id(reader)

    target_model_kind = reader.read_u8()

    if target_model_kind == REF_THIS_MODEL:
        model_uuid = imported_models["0"]["uuid"]
    elif target_model_kind == REF_OTHER_MODEL:
        modelref_kind = reader.read_u8()
        if modelref_kind != MODELREF_INDEX:
            raise ValueError("Expected MODELREF_INDEX")
        model_index = reader.read_u32()
        model_uuid = imported_models[str(model_index)]["uuid"]
    else:
        raise ValueError("Unknown target model kind")

    resolve_info = read_string(reader)

    return {
        "target_model": model_uuid,
        "target_node_id": target_node_id,
        "resolve_info": resolve_info,
    }
