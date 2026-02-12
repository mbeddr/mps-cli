from .constants import *
from .utils import read_string
from mpscli.model.SNode import SNode
from mpscli.model.SNodeRef import SNodeRef
from mpscli.model.builder.binary.node_id_utils import NodeIdEncodingUtils


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
    concept_index = reader.read_u16()
    concept = builder.index_2_concept[str(concept_index)]

    node_id = read_node_id(reader)
    node_id = NodeIdEncodingUtils.encode(node_id)

    aggregation_index = reader.read_u16()

    role_in_parent = None
    if parent is not None:
        role_in_parent = builder.index_2_child_role_in_parent.get(
            str(aggregation_index)
        )

    open_curly = reader.read_u8()
    if chr(open_curly) != "{":
        raise ValueError("Invalid node start")

    node = SNode(node_id, concept, role_in_parent, parent)

    properties_count = reader.read_u16()
    for _ in range(properties_count):
        prop_index = reader.read_u16()
        prop_name = builder.index_2_property[str(prop_index)]
        prop_value = read_string(reader)
        node.properties[prop_name] = prop_value

    user_objects_count = reader.read_u16()
    if user_objects_count != 0:
        raise ValueError("User objects not supported")

    references_count = reader.read_u16()

    for _ in range(references_count):
        ref_name, reference = read_reference(reader, builder, model)
        node.references[ref_name] = reference

    read_children(reader, builder, model, node)

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


def read_reference(reader, builder, model):
    reference_index = reader.read_u16()

    reference_name = builder.index_2_reference_role.get(str(reference_index))

    if reference_name is None:
        raise ValueError(f"Reference role not found for index {reference_index}")

    kind = reader.read_u8()

    if kind not in (1, 2, 3):
        raise ValueError(f"unknown reference kind: {kind}")

    if kind != 1:
        raise NotImplementedError(f"Reference kind {kind} not supported yet")

    target_node_id = read_node_id(reader)
    target_node_id = NodeIdEncodingUtils.encode(target_node_id)

    target_model_kind = reader.read_u8()

    if target_model_kind == REF_THIS_MODEL:
        model_uuid = model.uuid

    elif target_model_kind == REF_OTHER_MODEL:
        modelref_kind = reader.read_u8()

        if modelref_kind != MODELREF_INDEX:
            raise ValueError("Expected MODELREF_INDEX")

        model_index = reader.read_u32()
        model_uuid = builder.index_2_imported_model_uuid[str(model_index)]

    else:
        raise ValueError(f"Unknown target model kind: {target_model_kind}")

    resolve_info = read_string(reader)

    return reference_name, SNodeRef(
        model_uuid,
        target_node_id,
        resolve_info,
    )
