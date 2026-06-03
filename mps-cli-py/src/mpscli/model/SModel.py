import numpy as np

from mpscli.model.SNode import SNode
from mpscli.model.builder.utils.FlatModelPacker import (
    pack_strings,
    pack_properties,
    pack_references,
)


class SModel:
    # Two-phase designn: build then finalize
    #
    # During parsing, _add_node/_set_property/_set_reference fill plain Python list buffers (one entry per node).
    # Once parsing is done, _finalize() converts those buffers into flat numpy arrays and frees the buffers.
    #
    # The DFS pre-order guarante: every parser allocates a parent node before its children meaning
    # parent_buf[child_idx] < child_idx always holds true and _finalize() exploits this to build
    # first_child/next_sibling in a single forward pass without sorting or recursion.
    #
    # After finalize, SNode objects are thin views meaning they hold (model, idx) and read everything from the arrays
    # below via _get_node/_read_bytes. SNode objects are created on demand and cached by index so that any two
    # lookups for the same node always return the same Python object so this means the code that stores a
    # node reference and later compares it with another lookup will get the correct result.
    #
    # All arrays are saved to disk as .npz and loaded with mmap_mode='r' by ParseCache, so warm runs map the
    # file into virtual memory without reading bytes into RAM. Strings (uuids, property values) are packed as a flat
    # bytes blob with an int32 offset array: _read_bytes decodes a slice.
    # Properties and references use offset array (prop_start, ref_start) so so variable-length per-node data fits in
    # fixed-shape arrays.
    #
    # See storage layout below:
    #   _np_concept_idxs: index into _concepts_table
    #   _np_role_idxs: index into _roles_table, -1 = no role
    #   _np_parent_idxs: parent node index, -1 = root
    #   _np_first_child: first child index, -1 = leaf
    #   _np_next_sibling: next sibling index, -1 = last child
    #   _uuid_offsets: byte offsets into _uuid_data
    #   _uuid_data: packed UTF-8 uuid strings
    #   _prop_start: slice bounds into property arrays
    #   _prop_key_idxs: index into _prop_keys per property
    #   _prop_val_offsets: byte offsets into _prop_val_data
    #   _prop_val_data: packed UTF-8 property values
    #   _prop_keys: deduplicated key strings (100-200 entries)
    #   _ref_start: slice bounds into reference arrays
    #   _ref_key_idxs: index into _ref_keys per reference
    #   _ref_model_idxs: index into _ref_model_uuids per reference
    #   _ref_node_uuid_offsets: byte offsets into _ref_node_uuid_data
    #   _ref_node_uuid_data: packed node uuid strings
    #   _ref_resolve_offsets: byte offsets into _ref_resolve_data
    #   _ref_resolve_data: packed resolve_info strings
    #   _ref_keys: deduplicated role name strings
    #   _ref_model_uuids: deduplicated model uuid strings

    def __init__(self, name, uuid, is_do_not_generate):
        self.name = name
        self.uuid = uuid
        self.is_do_not_generate = is_do_not_generate
        self.path_to_model_file = ""

        # one entry per node and is grown during parsing then freed after _finalize()
        self._uuids = []
        self._concept_buf = []
        self._role_buf = []
        self._parent_buf = []
        self._properties = []
        self._references = []

        # concept and role dedup tables
        # each unique concept/role is stored once and nodes store an int32 index..
        # _concepts_map keys are id(concept) so we do not rely on __eq__
        self._concepts_table = []
        self._concepts_map = {}
        self._roles_table = []
        self._roles_map = {}

        # root node indices collected during parse and used by _build_root_nodes()
        self._root_idxs = []

        # {idx: SNode}: ensures the same object is returned for the same node
        self._node_cache = {}

        # these three dicts are built lazily on first use and never serialized
        self._uuid_index = None
        self._prop_key_lookup = None
        self._ref_key_lookup = None

        # flat numpy arrays, all None until _finalize() is called
        self._np_concept_idxs = None
        self._np_role_idxs = None
        self._np_parent_idxs = None
        self._np_first_child = None
        self._np_next_sibling = None
        self._uuid_offsets = None
        self._uuid_data = None
        self._prop_start = None
        self._prop_key_idxs = None
        self._prop_val_offsets = None
        self._prop_val_data = None
        self._prop_keys = None
        self._ref_start = None
        self._ref_key_idxs = None
        self._ref_model_idxs = None
        self._ref_node_uuid_offsets = None
        self._ref_node_uuid_data = None
        self._ref_resolve_offsets = None
        self._ref_resolve_data = None
        self._ref_keys = None
        self._ref_model_uuids = None

        self._finalized = False

        # populatedd by _build_root_nodes() at the end of _finalize()
        self.root_nodes = []

    # ------------------------------------------------------------------
    # builder API - called by parsers during the build phase
    # ------------------------------------------------------------------

    def _add_node(self, uuid, concept, role, parent_idx):
        # allocates a new node slot and returns its integer index where parent_idx is an int or None (None means this is a root node)..
        #
        # some low-level tests call read_node() on raw bytes after build() has already finalized the model and they
        # need a builder context but do not really maybe care about the full model and to support this
        # re-entering build phase after _finalize() is allowed so tat buffers are restored and the new nodes
        # are not reflected in the finalized arrays
        if self._concept_buf is None:
            self._concept_buf = []
            self._role_buf = []
            self._parent_buf = []
            self._properties = []
            self._references = []
            self._node_cache = {}
            if self._uuids is None:
                self._uuids = []
        idx = len(self._uuids)
        self._uuids.append(uuid)

        # store concept by index into _concepts_table to avoid duplicating the same SConcept object
        # across all nodes that share a concept type
        key = id(concept)
        if key not in self._concepts_map:
            self._concepts_map[key] = len(self._concepts_table)
            self._concepts_table.append(concept)
        self._concept_buf.append(self._concepts_map[key])

        # same dedup approach for role strings
        if role is None:
            self._role_buf.append(-1)
        else:
            if role not in self._roles_map:
                self._roles_map[role] = len(self._roles_table)
                self._roles_table.append(role)
            self._role_buf.append(self._roles_map[role])

        self._parent_buf.append(-1 if parent_idx is None else parent_idx)
        self._properties.append({})
        self._references.append({})
        return idx

    def _set_property(self, idx, key, value):
        self._properties[idx][key] = value

    def _set_reference(self, idx, key, ref):
        self._references[idx][key] = ref

    # ------------------------------------------------------------------
    # finalize - called once by each parser after all nodes are built
    # ------------------------------------------------------------------
    def _finalize(self):
        if self._finalized:
            return
        n = len(self._uuids)
        empty = np.empty(0, dtype=np.int32)

        # models with no nodes still need valid (empty) arrays so that  _read_bytes and slice logic work
        # without None checks
        if n == 0:
            self._np_concept_idxs = empty
            self._np_role_idxs = empty
            self._np_parent_idxs = empty
            self._np_first_child = empty
            self._np_next_sibling = empty
            self._uuid_offsets = np.zeros(1, dtype=np.int32)
            self._uuid_data = b""
            self._prop_start = np.zeros(1, dtype=np.int32)
            self._prop_key_idxs = empty
            self._prop_val_offsets = np.zeros(1, dtype=np.int32)
            self._prop_val_data = b""
            self._prop_keys = []
            self._ref_start = np.zeros(1, dtype=np.int32)
            self._ref_key_idxs = empty
            self._ref_model_idxs = empty
            self._ref_node_uuid_offsets = np.zeros(1, dtype=np.int32)
            self._ref_node_uuid_data = b""
            self._ref_resolve_offsets = np.zeros(1, dtype=np.int32)
            self._ref_resolve_data = b""
            self._ref_keys = []
            self._ref_model_uuids = []
            self._finalized = True
            self._build_root_nodes()
            return

        # structural int32 arrays - one value per node
        self._np_concept_idxs = np.array(self._concept_buf, dtype=np.int32)
        self._np_role_idxs = np.array(self._role_buf, dtype=np.int32)
        self._np_parent_idxs = np.array(self._parent_buf, dtype=np.int32)

        # build first_child/next_sibling linked lists in one forward pass and also parsers allocate a parent
        # before any of its children
        first_child = np.full(n, -1, dtype=np.int32)
        next_sibling = np.full(n, -1, dtype=np.int32)
        last_child = np.full(n, -1, dtype=np.int32)

        parent_buf = self._parent_buf
        for ci in range(n):
            pi = parent_buf[ci]
            if pi == -1:
                continue
            if first_child[pi] == -1:
                first_child[pi] = ci
            else:
                next_sibling[last_child[pi]] = ci
            last_child[pi] = ci

        self._np_first_child = first_child
        self._np_next_sibling = next_sibling

        # pack strings, properties and references - see FlatModelPacker for format details
        self._uuid_offsets, self._uuid_data = pack_strings(
            [u or "" for u in self._uuids]
        )
        (
            self._prop_start,
            self._prop_key_idxs,
            self._prop_val_offsets,
            self._prop_val_data,
            self._prop_keys,
        ) = pack_properties(self._properties)

        (
            self._ref_start,
            self._ref_key_idxs,
            self._ref_model_idxs,
            self._ref_node_uuid_offsets,
            self._ref_node_uuid_data,
            self._ref_resolve_offsets,
            self._ref_resolve_data,
            self._ref_keys,
            self._ref_model_uuids,
        ) = pack_references(self._references)

        # all data is now in flat arrays so free the build buffers
        self._uuids = None
        self._concept_buf = None
        self._role_buf = None
        self._parent_buf = None
        self._properties = None
        self._references = None
        self._concepts_map = {}
        self._roles_map = {}

        self._finalized = True
        self._build_root_nodes()

    def _build_root_nodes(self):
        # SNode objects are created on demand where root_nodes are the entry points so that callers hold
        # onto directly and we create them here rather than waiting for a traversal to trigger lazy creation
        self.root_nodes = [self._get_node(i) for i in self._root_idxs]

    def _get_node(self, idx):
        # returns the same SNode instance every time for a given index so that node identity is stable - two lookups for node 42 always give back
        # the same Python object since the first call creates and caches it..
        node = self._node_cache.get(idx)
        if node is None:

            node = SNode(self, idx)
            self._node_cache[idx] = node
        return node

    def _read_bytes(self, data, offsets, idx):
        # reads one packed string entry from a bytes blob and offsets[idx] and offsets[idx+1] give the
        # start and end byte positions. numpy uint8 slices need .tobytes() before decode but plain Python bytes
        # slices decode directly.
        start = int(offsets[idx])
        end = int(offsets[idx + 1])
        if start == end:
            return ""
        chunk = data[start:end]
        if hasattr(chunk, "tobytes"):
            return chunk.tobytes().decode()
        return chunk.decode()

    def _get_prop_key_idx(self, key):
        # builds the reverse lookup dict on first call, then returns the index of the given key in _prop_keys,
        # or -1 if not found
        if self._prop_key_lookup is None:
            self._prop_key_lookup = {k: i for i, k in enumerate(self._prop_keys)}
        return self._prop_key_lookup.get(key, -1)

    def _get_ref_key_idx(self, role):
        # same as _get_prop_key_idx but for reference role names
        if self._ref_key_lookup is None:
            self._ref_key_lookup = {k: i for i, k in enumerate(self._ref_keys)}
        return self._ref_key_lookup.get(role, -1)

    def get_nodes(self):
        res = []
        for root in self.root_nodes:
            res.append(root)
            res.extend(root.get_descendants())
        return res

    def get_node_by_uuid(self, target_uuid):
        # builds a uuid -> index dict on first call is most likely O(n) and then O(1) for every subsequent call I
        # guess.
        if self._uuid_index is None:
            n = len(self._uuid_offsets) - 1
            self._uuid_index = {
                self._read_bytes(self._uuid_data, self._uuid_offsets, i): i
                for i in range(n)
            }
        idx = self._uuid_index.get(target_uuid)
        if idx is None:
            raise KeyError(target_uuid)
        return self._get_node(idx)
