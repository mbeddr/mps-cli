from .constants import *
from mpscli.model.SNode import SNode
from mpscli.model.SNodeRef import SNodeRef
from mpscli.model.builder.binary.node_id_utils import NodeIdEncodingUtils

NODE_ID_ENCODER = NodeIdEncodingUtils()


def read_children(reader, builder, model, parent=None):

    child_count = reader.read_u32()

    nodes = []

    for _ in range(child_count):

        node = read_node(reader, builder, model, parent)

        if parent is None:
            model.root_nodes.append(node)
        else:
            parent.children.append(node)

        nodes.append(node)

    return nodes


def read_node(reader, builder, model, parent=None):

    pos = reader.tell()

    node_id = read_node_id(reader)

    concept_id = str(reader.read_u64())

    concept = builder.concept_id_2_concept.get(concept_id)

    if concept is None:
        raise RuntimeError(f"Unknown concept id {concept_id} at stream position {pos}")

    aggregation_index = reader.read_u16()

    role_in_parent = None

    if parent is not None:
        role_in_parent = builder.index_2_child_role_in_parent.get(aggregation_index)

    open_curly = reader.read_u8()

    if chr(open_curly) != "{":
        raise RuntimeError(f"Invalid node start at {reader.tell()}")

    node = SNode(node_id, concept, role_in_parent, parent)

    # -------------------------
    # PROPERTIES
    # -------------------------

    properties_count = reader.read_u16()

    for _ in range(properties_count):

        prop_index = reader.read_u16()

        prop_name = builder.index_2_property.get(prop_index)

        prop_value = reader.read_string()

        if prop_name:
            node.properties[prop_name] = prop_value

    # -------------------------
    # USER OBJECTS
    # -------------------------

    user_objects_count = reader.read_u16()

    for _ in range(user_objects_count):
        reader.read_string()

    # -------------------------
    # REFERENCES
    # -------------------------

    references_count = reader.read_u16()

    for _ in range(references_count):

        ref_name, reference = read_reference(reader, builder, model)

        if ref_name:
            node.references[ref_name] = reference

    # -------------------------
    # CHILDREN
    # -------------------------

    read_children(reader, builder, model, node)

    closed_curly = reader.read_u8()

    if chr(closed_curly) != "}":
        raise RuntimeError(f"Invalid node end at {reader.tell()}")

    return node


def read_node_id(reader):

    kind = reader.read_u8()

    if kind == 0:
        return None

    if kind == NODEID_LONG:

        raw_id = str(reader.read_u64())

        return NODE_ID_ENCODER.encode(raw_id)

    if kind == NODEID_STRING:

        return reader.read_string()

    raise RuntimeError(f"Unknown node id kind: {kind}")


def read_reference(reader, builder, model):

    reference_index = reader.read_u16()

    reference_name = builder.index_2_reference_role.get(reference_index)

    reader.read_u8()

    target_node_id = read_node_id(reader)

    target_model_kind = reader.read_u8()

    if target_model_kind == REF_THIS_MODEL:

        model_uuid = model.uuid

    elif target_model_kind == REF_OTHER_MODEL:

        reader.read_u8()

        model_index = reader.read_u32()

        model_uuid = builder.index_2_imported_model_uuid.get(model_index)

    else:

        model_uuid = None

    resolve_info = reader.read_string()

    return reference_name, SNodeRef(
        model_uuid,
        target_node_id,
        resolve_info,
    )
