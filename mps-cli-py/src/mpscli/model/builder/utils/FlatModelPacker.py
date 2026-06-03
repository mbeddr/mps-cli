# mpscli/model/builder/utils/FlatModelPacker.py
#
# Serialization helpers for SModel's flat array storage. This is called by SModel._finalize() to
# convert Python dicts into compact numpy arrays suitable for memory mapping on warm cache loads.
#

import numpy as np


def pack_strings(strings):
    """
    Pack a list of strings into a bytes blob with int32 byte offsets

    offsets[i] to offsets[i+1] is the UTF-8 encoded slice for string i. The resulting arrays are
    numpy-memmappable so on warm cache load they are mapped into virtual memory with np.load(mmap_mode='r') and
    individual strings are decoded on first access only.

    Returns (offsets int32[n+1], data bytes)
    """
    encoded = [s.encode() for s in strings]
    n = len(encoded)
    offsets = np.zeros(n + 1, dtype=np.int32)
    for i, b in enumerate(encoded):
        offsets[i + 1] = offsets[i] + len(b)
    return offsets, b"".join(encoded)


def pack_properties(properties):
    """
    Pack a list of per node property dicts into flat arrayss

    layout explanation:
      prop_start[i] to prop_start[i+1] is the slice of property entries for node i. Property keys are deduplicated
      across all nodes because the same key (ex: 'name','abstract', 'visibility') appears on millions of nodes
      so storing a single int32 index per occurrence instead of the full string saves significant memory in my opinion.
      Property values are stored as a packed bytes blob with int32 byte offsets because values vary significantly
      in length and cannot fit in a fixed-width array right?

    Returns:
      prop_start: int32[n+1] which is per-node slice bounds
      prop_key_idxs: int32[p] - key index into prop_keys
      prop_val_offsets: int32[p+1] -  byte offsets into prop_val_data
      prop_val_data: bytes - packed UTF-8 property values
      prop_keys: list[str] - deduplicated key names (small, around 100-200 entries maybe)
    """
    n = len(properties)
    prop_keys = []
    prop_key_map = {}
    prop_start = np.zeros(n + 1, dtype=np.int32)
    key_idxs = []
    val_encoded = []
    total = 0
    for node_idx, d in enumerate(properties):
        prop_start[node_idx] = total
        for k, v in d.items():
            if k not in prop_key_map:
                prop_key_map[k] = len(prop_keys)
                prop_keys.append(k)
            key_idxs.append(prop_key_map[k])
            val_encoded.append((str(v) if v is not None else "").encode())
            total += 1
    prop_start[n] = total
    empty = np.empty(0, dtype=np.int32)
    prop_key_idxs = np.array(key_idxs, dtype=np.int32) if key_idxs else empty
    val_offsets = np.zeros(total + 1, dtype=np.int32)
    for i, b in enumerate(val_encoded):
        val_offsets[i + 1] = val_offsets[i] + len(b)
    return prop_start, prop_key_idxs, val_offsets, b"".join(val_encoded), prop_keys


def pack_references(references):
    """
    Pack a list of per-node reference dicts into flat arrays..

    Each SNodeRef has three string fields: model_uuid, node_uuid, and resolve_info. model_uuid is deduplicated
    because a model typically references a small set of other modelss and the same model UUID appears on many
    references so an int32 index into a lookup table is much cheaper I think than repeating the full string..
    node_uuid and resolve_info are stored as separate packed bytes blobs because each reference points to a
    distinct node and these values are rarely repeated

    Returns:
      ref_start: int32[n+1] - per-node slice bounds
      ref_key_idxs: int32[r] - role name index into ref_keys
      ref_model_idxs: int32[r] - model UUID index into ref_model_uuids
      ref_node_uuid_offsets: int32[r+1] - byte offsets into ref_node_uuid_data
      ref_node_uuid_data: bytes
      ref_resolve_offsets: int32[r+1] - byte offsets into ref_resolve_data
      ref_resolve_data: bytes
      ref_keys: list[str] - deduplicated role names (small)
      ref_model_uuids: list[str] - deduplicated model UUIDs (small)
    """
    n = len(references)
    ref_keys = []
    ref_key_map = {}
    ref_model_uuids = []
    ref_model_uuid_map = {}
    ref_start = np.zeros(n + 1, dtype=np.int32)
    key_idxs = []
    model_idxs = []
    node_uuid_encoded = []
    resolve_encoded = []
    total = 0
    for node_idx, d in enumerate(references):
        ref_start[node_idx] = total
        for role, ref in d.items():
            if role not in ref_key_map:
                ref_key_map[role] = len(ref_keys)
                ref_keys.append(role)
            key_idxs.append(ref_key_map[role])
            model_uuid = ref.model_uuid or ""
            if model_uuid not in ref_model_uuid_map:
                ref_model_uuid_map[model_uuid] = len(ref_model_uuids)
                ref_model_uuids.append(model_uuid)
            model_idxs.append(ref_model_uuid_map[model_uuid])
            node_uuid_encoded.append((ref.node_uuid or "").encode())
            resolve_encoded.append((ref.resolve_info or "").encode())
            total += 1
    ref_start[n] = total
    empty = np.empty(0, dtype=np.int32)
    ref_key_idxs = np.array(key_idxs, dtype=np.int32) if key_idxs else empty
    ref_model_idxs_arr = np.array(model_idxs, dtype=np.int32) if model_idxs else empty
    node_uuid_offsets = np.zeros(total + 1, dtype=np.int32)
    for i, b in enumerate(node_uuid_encoded):
        node_uuid_offsets[i + 1] = node_uuid_offsets[i] + len(b)
    resolve_offsets = np.zeros(total + 1, dtype=np.int32)
    for i, b in enumerate(resolve_encoded):
        resolve_offsets[i + 1] = resolve_offsets[i] + len(b)
    return (
        ref_start,
        ref_key_idxs,
        ref_model_idxs_arr,
        node_uuid_offsets,
        b"".join(node_uuid_encoded),
        resolve_offsets,
        b"".join(resolve_encoded),
        ref_keys,
        ref_model_uuids,
    )
