from mpscli.model.SNode import SNode
from mpscli.model.SNodeRef import SNodeRef
from mpscli.model.builder.utils.NodeIdEncodingUtils import NodeIdEncodingUtils
from mpscli.model.builder.binary.constants import (
    NULL,
    NODEID_LONG,
    NODEID_STRING,
    REF_THIS_MODEL,
    REF_OTHER_MODEL,
    NODE_OPEN_BRACE,
    NODE_CLOSE_BRACE,
    AGG_INDEX_NONE,
    MODELREF_INDEX,
    MODELID_REGULAR,
    MODELID_FOREIGN,
    MODULEID_REGULAR,
    MODULEID_FOREIGN,
    MODULEREF_MODULEID,
    MODULEREF_NAMEONLY,
    MODULEREF_INDEX,
)
from mpscli.model.builder.binary.uuid_utils import uuid_str

# Java class structure vs Python structure - see below info to understand important context
# Java has a two-level class hierarchy for node reading:
#
#   BareNodeReader (base class)
#    Handles raw concept/nodeId/containmentLink reading via ModelInputStream's own inline/indexed
#    caches (readConcept(), readNodeId(), readContainmentLink()) used for I guess standalone node serialization
#    source: https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BareNodeReader.java
#   NodesReader extends BareNodeReader
#    Overrides instantiate(), readProperties(), readReferences() to use ReadHelper index maps built from the registry
#    section, instead of ModelInputStream's own caches.
#    This is the class used for full model loading in BinaryPersistence.loadModel().
#    source: https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/NodesReader.java

# Python has no BareNodeReader equivalent.
# our read_node() + read_children() implement only the NodesReader pattern using builder.index_2_concept,
# builder.index_2_property etc... to look up concepts and properties by their u16 registry indices
# We do not reallyy need the standalone BareNodeReader use case (such as clipboard or undo) for CLI extraction

NODE_ID_ENCODER = NodeIdEncodingUtils()


def read_children(reader, builder, model, parent=None):
    # mirrors BareNodeReader.readChildren() in:
    # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BareNodeReader.java
    child_count = reader.read_u32()

    for _ in range(child_count):
        node = read_node(reader, builder, model, parent)

        if parent is None:
            model.root_nodes.append(node)
        else:
            parent.children.append(node)

    return model.root_nodes if parent is None else parent.children


def read_node(reader, builder, model, parent=None):
    # Mirrors the combined logic of BareNodeReader.readNode() and NodesReader.instantiate()
    # in https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BareNodeReader.java
    # and https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/NodesReader.java
    #
    # Python read_node() flattens instantiate() inline so no subclass needed and the ReadHelper index maps
    # are accessed directly via builder.index_2_*

    pos = reader.tell()

    # u16 concept index - looked up in builder.index_2_concept
    concept_index = reader.read_u16()
    concept = builder.index_2_concept.get(concept_index)
    if concept is None:
        raise RuntimeError(f"Unknown concept index {concept_index} at pos {pos}")

    # node id - kind byte dispatch
    node_id = _read_node_id(reader)

    agg_index = reader.read_u16()
    role_in_parent = None
    if parent is not None and agg_index != AGG_INDEX_NONE:
        role_in_parent = builder.index_2_child_role_in_parent.get(agg_index)

    brace = reader.read_u8()
    if brace != NODE_OPEN_BRACE:
        raise RuntimeError(
            f"Expected '{{' (0x{NODE_OPEN_BRACE:02X}) at pos {reader.tell() - 1}, got 0x{brace:02X}"
        )

    node = SNode(node_id, concept, role_in_parent, parent)

    props_count = reader.read_u16()
    for _ in range(props_count):
        prop_index = reader.read_u16()
        value = reader.read_string()
        prop_key = builder.index_2_property.get(prop_index)
        if prop_key is not None:
            node.properties[prop_key] = value

    user_obj_count = reader.read_u16()
    for _ in range(user_obj_count):
        reader.read_string()

    refs_count = reader.read_u16()
    for _ in range(refs_count):
        ref_name, ref = _read_reference(reader, builder, model)
        if ref_name is not None:
            node.references[ref_name] = ref

    # read children recursively
    read_children(reader, builder, model, node)

    brace = reader.read_u8()
    if brace != NODE_CLOSE_BRACE:
        raise RuntimeError(
            f"Expected '}}' (0x{NODE_CLOSE_BRACE:02X}) at pos {reader.tell() - 1}, got 0x{brace:02X}"
        )

    return node


def _read_node_id(reader):
    # mirrors ModelInputStream.readNodeId() in:
    # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/kernel/source/jetbrains/mps/util/io/ModelInputStream.java
    #
    # NODEID_LONG (0x18) - integer node id read as u64 andd then encoded by NodeIdEncodingUtils into MPS's compact
    # base-64 string form. Java's regular(long) stores the raw long but our Python implementation encodes it
    # immediately to match MPS's display format.

    kind = reader.read_u8()

    if kind == NULL:
        return None

    if kind == NODEID_LONG:
        raw = str(reader.read_u64())
        return NODE_ID_ENCODER.encode(raw)

    if kind == NODEID_STRING:
        return reader.read_string()

    raise RuntimeError(f"Unknown node id kind 0x{kind:02X} at pos {reader.tell() - 1}")


def _read_reference(reader, builder, model):
    # mirrors NodesReader.readReferences() and BareNodeReader.readReference() in:
    # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/NodesReader.java and
    # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BareNodeReader.java
    #
    # Python simplification: we always read kind byte but only handle kind==1 (static ref with nodeId) by far the
    # most common case in model files. kind==2 (dynamic unresolved) and kind==3 (dynamic with generator origin)
    # do not appear in standard persisted models.
    # The skip byte read below corresponds to kind==1 in Java.
    #
    # For model-kind:
    #   REF_THIS_MODEL (0x11): target is in the current model so use model.uuid
    #   REF_OTHER_MODEL (0x12): target is in an imported model so resolve via import index

    ref_index = reader.read_u16()
    ref_name = builder.index_2_reference_role.get(ref_index)

    # kind byte - always 0x01 in persisted model files
    reader.read_u8()

    target_node_id = _read_node_id(reader)

    model_kind = reader.read_u8()

    if model_kind == REF_THIS_MODEL:
        model_uuid = model.uuid

    elif model_kind == REF_OTHER_MODEL:
        model_uuid = _read_other_model_ref(reader, builder)

    else:
        # unknown model kind - consume the resolve_info string and return a placeholder
        reader.read_string()
        return ref_name, SNodeRef(None, target_node_id, None)

    resolve_info = reader.read_string()

    return ref_name, SNodeRef(model_uuid, target_node_id, resolve_info)


def _read_other_model_ref(reader, builder):
    # reads the model reference that follows a REF_OTHER_MODEL (0x12) byte in a node reference
    inner_kind = reader.read_u8()

    if inner_kind == MODELREF_INDEX:
        # most common case is import table lookup
        import_index = reader.read_u32()
        return builder.index_2_imported_model_uuid.get(str(import_index))

    elif inner_kind == 0x07:
        # full V2 model reference (inline, not from import table)
        sub = reader.read_u8()

        if sub == MODELID_REGULAR:
            uuid = reader.read_uuid()
            model_id = uuid_str(uuid[0], uuid[1])
            # model long name
            reader.read_string()
            # declaring module ref - Java's https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/kernel/source/jetbrains/mps/util/io/ModelInputStream.java
            # calls readModuleReference() heree and not a second string
            _read_module_ref(reader)

        elif sub == MODELID_FOREIGN:
            # foreign model id, ex: "java:java.lang"
            reader.read_string()
            # model name, ex: "java.lang@java_stub"
            reader.read_string()
            _read_module_ref(reader)
            model_id = ""

        elif sub == NULL:
            model_id = ""

        else:
            raise RuntimeError(
                f"Unsupported model ref sub-kind 0x{sub:02X} at pos {reader.tell()}"
            )
        return model_id

    elif inner_kind == NULL:
        return None

    else:
        raise RuntimeError(
            f"Unknown model ref inner kind 0x{inner_kind:02X} at pos {reader.tell() - 1}"
        )


def _read_module_ref(reader):
    kind = reader.read_u8()
    if kind == NULL:
        return
    if kind == MODULEREF_MODULEID:
        sub = reader.read_u8()
        if sub == MODULEID_REGULAR:
            reader.read_uuid()
        elif sub == MODULEID_FOREIGN:
            reader.read_string()
        reader.read_string()
    elif kind == MODULEREF_NAMEONLY:
        reader.read_string()
    elif kind == MODULEREF_INDEX:
        reader.read_u32()
    else:
        raise RuntimeError(
            f"Unknown module_ref kind 0x{kind:02X} at pos {reader.tell() - 1}"
        )
