from mpscli.model.SNode import SNode
from mpscli.model.SNodeRef import SNodeRef
from mpscli.model.builder.binary.node_id_utils import NodeIdEncodingUtils

NODE_ID_ENCODER = NodeIdEncodingUtils()

# 8-byte integer id
NODEID_REGULAR = 0x18
# string-encoded id (used for foreign/external node ids)
NODEID_STRING = 0x17
NODEID_NULL = 0x70

REF_THIS_MODEL = 0x11
REF_OTHER_MODEL = 0x12


def read_children(reader, builder, model, parent=None):
    child_count = reader.read_u32()

    for _ in range(child_count):
        node = read_node(reader, builder, model, parent)

        if parent is None:
            model.root_nodes.append(node)
        else:
            parent.children.append(node)

    return model.root_nodes if parent is None else parent.children


def read_node(reader, builder, model, parent=None):
    pos = reader.tell()

    concept_index = reader.read_u16()
    concept = builder.index_2_concept.get(concept_index)
    if concept is None:
        raise RuntimeError(f"Unknown concept index {concept_index} at pos {pos}")

    node_id = _read_node_id(reader)

    agg_index = reader.read_u16()
    role_in_parent = None
    if parent is not None and agg_index != 0xFFFF:
        role_in_parent = builder.index_2_child_role_in_parent.get(agg_index)

    brace = reader.read_u8()
    if brace != 0x7B:
        raise RuntimeError(
            f"Expected '{{' (0x7B) at pos {reader.tell() - 1}, got 0x{brace:02X}"
        )

    node = SNode(node_id, concept, role_in_parent, parent)

    props_count = reader.read_u16()
    for _ in range(props_count):
        prop_index = reader.read_u16()
        value = reader.read_string()
        prop_key = builder.index_2_property.get(prop_index)
        if prop_key is not None:
            node.properties[prop_key] = value

    # V2 format
    user_obj_count = reader.read_u16()
    for _ in range(user_obj_count):
        reader.read_string()

    refs_count = reader.read_u16()
    for _ in range(refs_count):
        ref_name, ref = _read_reference(reader, builder, model)
        if ref_name is not None:
            node.references[ref_name] = ref

    # recursive children call
    read_children(reader, builder, model, node)

    brace = reader.read_u8()
    if brace != 0x7D:
        raise RuntimeError(
            f"Expected '}}' (0x7D) at pos {reader.tell() - 1}, got 0x{brace:02X}"
        )

    return node


def _read_node_id(reader):
    kind = reader.read_u8()

    if kind == NODEID_NULL:
        return None

    if kind == NODEID_REGULAR:
        raw = str(reader.read_u64())
        return NODE_ID_ENCODER.encode(raw)

    if kind == NODEID_STRING:
        return reader.read_string()

    raise RuntimeError(f"Unknown node id kind 0x{kind:02X} at pos {reader.tell() - 1}")


def _read_reference(reader, builder, model):
    ref_index = reader.read_u16()
    ref_name = builder.index_2_reference_role.get(ref_index)

    # skip byte (always 0x01)
    reader.read_u8()

    target_node_id = _read_node_id(reader)

    model_kind = reader.read_u8()

    if model_kind == REF_THIS_MODEL:
        model_uuid = model.uuid

    elif model_kind == REF_OTHER_MODEL:
        model_uuid = _read_other_model_ref(reader, builder)

    else:
        reader.read_string()
        return ref_name, SNodeRef(None, target_node_id, None)

    resolve_info = reader.read_string()

    return ref_name, SNodeRef(model_uuid, target_node_id, resolve_info)


def _read_other_model_ref(reader, builder):
    inner_kind = reader.read_u8()

    # indexed — u32 import table index
    if inner_kind == 0x09:
        import_index = reader.read_u32()
        return builder.index_2_imported_model_uuid.get(str(import_index))

    # full V2 model reference
    elif inner_kind == 0x07:
        sub = reader.read_u8()
        # regular (uuid-based)
        if sub == 0x28:
            uuid = reader.read_uuid()
            model_id = f"r:{uuid[0]:016x}{uuid[1]:016x}"
            # model long name
            reader.read_string()
            # stereotype (null)
            reader.read_string()
        elif sub == 0x26:
            # foreign model id, example 'java:java.lang'
            reader.read_string()
            # model name, example "java.lang@java_stub"
            reader.read_string()
            _read_module_ref(reader)
            model_id = ""
        elif sub == 0x70:
            model_id = ""
        else:
            raise RuntimeError(
                f"Unsupported model ref sub-kind 0x{sub:02X} at pos {reader.tell()}"
            )
        return model_id

    elif inner_kind == 0x70:
        return None

    else:
        raise RuntimeError(
            f"Unknown model ref inner kind 0x{inner_kind:02X} at pos {reader.tell() - 1}"
        )


def _read_module_ref(reader):
    kind = reader.read_u8()
    if kind == 0x70:
        return
    if kind == 0x17:
        sub = reader.read_u8()
        if sub == 0x48:
            reader.read_uuid()
        elif sub == 0x47:
            reader.read_string()
        reader.read_string()
    elif kind == 0x18:
        reader.read_string()
    elif kind == 0x19:
        reader.read_u32()
    else:
        raise RuntimeError(
            f"Unknown module_ref kind 0x{kind:02X} at pos {reader.tell() - 1}"
        )
