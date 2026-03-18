from mpscli.model.SNode import SNode
from mpscli.model.SNodeRef import SNodeRef
from mpscli.model.builder.binary.node_id_utils import NodeIdEncodingUtils

NODE_ID_ENCODER = NodeIdEncodingUtils()

# ── Node-id kind bytes ───────────────────────────────────────────────────────
NODEID_REGULAR = 0x18  # 8-byte integer id
NODEID_STRING = 0x17  # string-encoded id (used for foreign/external node ids)
NODEID_NULL = 0x70  # null

# ── Model-reference kind bytes (in reference entries) ───────────────────────
REF_THIS_MODEL = 0x11  # target is in the current model — no extra bytes
REF_OTHER_MODEL = 0x12  # target is in an imported model — extra u8 + u32 follow

# ────────────────────────────────────────────────────────────────────────────


def read_children(reader, builder, model, parent=None):
    """
    Reads a child-list: u32 count followed by that many readNode() calls.
    Root-level nodes are appended to model.root_nodes.
    Child nodes are appended to parent.children.
    """
    child_count = reader.read_u32()

    for _ in range(child_count):
        node = read_node(reader, builder, model, parent)

        if parent is None:
            model.root_nodes.append(node)
        else:
            parent.children.append(node)

    return model.root_nodes if parent is None else parent.children


def read_node(reader, builder, model, parent=None):
    """
    Reads a single node.  See module docstring for the byte layout.
    """
    pos = reader.tell()

    # ── concept ──────────────────────────────────────────────────────────────
    concept_index = reader.read_u16()
    concept = builder.index_2_concept.get(concept_index)
    if concept is None:
        raise RuntimeError(f"Unknown concept index {concept_index} at pos {pos}")

    # ── node id ───────────────────────────────────────────────────────────────
    node_id = _read_node_id(reader)

    # ── role in parent ────────────────────────────────────────────────────────
    agg_index = reader.read_u16()
    role_in_parent = None
    if parent is not None and agg_index != 0xFFFF:
        role_in_parent = builder.index_2_child_role_in_parent.get(agg_index)

    # ── opening brace ─────────────────────────────────────────────────────────
    brace = reader.read_u8()
    if brace != 0x7B:
        raise RuntimeError(
            f"Expected '{{' (0x7B) at pos {reader.tell() - 1}, got 0x{brace:02X}"
        )

    node = SNode(node_id, concept, role_in_parent, parent)

    # ── properties ────────────────────────────────────────────────────────────
    props_count = reader.read_u16()
    for _ in range(props_count):
        prop_index = reader.read_u16()
        value = reader.read_string()
        prop_key = builder.index_2_property.get(prop_index)
        if prop_key is not None:
            node.properties[prop_key] = value

    # ── user objects ──────────────────────────────────────────────────────────
    user_obj_count = reader.read_u16()
    for _ in range(user_obj_count):
        reader.read_string()  # key
        reader.read_string()  # value

    # ── references ────────────────────────────────────────────────────────────
    refs_count = reader.read_u16()
    for _ in range(refs_count):
        ref_name, ref = _read_reference(reader, builder, model)
        if ref_name is not None:
            node.references[ref_name] = ref

    # ── children (recursive) ─────────────────────────────────────────────────
    read_children(reader, builder, model, node)

    # ── closing brace ─────────────────────────────────────────────────────────
    brace = reader.read_u8()
    if brace != 0x7D:
        raise RuntimeError(
            f"Expected '}}' (0x7D) at pos {reader.tell() - 1}, got 0x{brace:02X}"
        )

    return node


# ── Helpers ──────────────────────────────────────────────────────────────────


def _read_node_id(reader):
    """
    Reads a node id:
        0x18 → Regular long id  → encode with NodeIdEncodingUtils
        0x17 → Foreign string   → return raw string
        0x70 → NULL             → return None
    """
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
    """
    Reads one reference entry:

        ref_index   u16
        skip        u8   (always 0x01)
        node_id_kind + node_id   (same as _read_node_id)
        model_kind  u8
            0x11 REF_THIS_MODEL  → no extra bytes
            0x12 REF_OTHER_MODEL → u8 extra + u32 model_index
        resolve_info  string

    Returns (ref_name, SNodeRef) or (None, None) on unknown index.
    """
    ref_index = reader.read_u16()
    ref_name = builder.index_2_reference_role.get(ref_index)

    reader.read_u8()  # skip byte (always 0x01)

    target_node_id = _read_node_id(reader)

    model_kind = reader.read_u8()

    if model_kind == REF_THIS_MODEL:
        model_uuid = model.uuid

    elif model_kind == REF_OTHER_MODEL:
        reader.read_u8()  # extra byte
        model_index = reader.read_u32()
        model_uuid = builder.index_2_imported_model_uuid.get(str(model_index))

    else:
        # Unknown model kind — consume resolve_info and return placeholder
        reader.read_string()
        return ref_name, SNodeRef(None, target_node_id, None)

    resolve_info = reader.read_string()

    return ref_name, SNodeRef(model_uuid, target_node_id, resolve_info)
