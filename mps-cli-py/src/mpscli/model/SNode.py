class SNode:
    # A node view that holds only a reference to its model and an integer index..
    # All data (uuid, concept, properties, children) lives in SModel's flat numpy arrays and is read on demand.
    # So basicallyy nothing is stored in the node itself
    __slots__ = ("_model", "_idx")

    def __init__(self, model, idx):
        self._model = model
        self._idx = idx

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, SNode):
            return NotImplemented
        return self._model is other._model and self._idx == other._idx

    def __hash__(self):
        # model identity via id() is stable for the lifetime of a parse run
        return hash((id(self._model), self._idx))

    @property
    def uuid(self):
        m = self._model
        return m._read_bytes(m._uuid_data, m._uuid_offsets, self._idx)

    @property
    def concept(self):
        return self._model._concepts_table[int(self._model._np_concept_idxs[self._idx])]

    @property
    def role_in_parent(self):
        r = int(self._model._np_role_idxs[self._idx])
        return None if r == -1 else self._model._roles_table[r]

    @property
    def parent(self):
        p = int(self._model._np_parent_idxs[self._idx])
        return None if p == -1 else self._model._get_node(p)

    @property
    def properties(self):
        # builds a fresh dict from this node's property slice in the model arrays
        # if we need only one property then I guess get_property() is faster because it scans the slice directly
        # without building the full dict
        m = self._model
        i = self._idx
        start = int(m._prop_start[i])
        end = int(m._prop_start[i + 1])
        result = {}
        for j in range(start, end):
            key = m._prop_keys[int(m._prop_key_idxs[j])]
            val = m._read_bytes(m._prop_val_data, m._prop_val_offsets, j)
            result[key] = val
        return result

    @property
    def references(self):
        # builds a fresh dict from this node's reference slice in the model arrays
        from mpscli.model.SNodeRef import SNodeRef

        m = self._model
        i = self._idx
        start = int(m._ref_start[i])
        end = int(m._ref_start[i + 1])
        result = {}
        for j in range(start, end):
            role = m._ref_keys[int(m._ref_key_idxs[j])]
            model_uuid = m._ref_model_uuids[int(m._ref_model_idxs[j])]
            node_uuid = m._read_bytes(
                m._ref_node_uuid_data, m._ref_node_uuid_offsets, j
            )
            resolve = m._read_bytes(m._ref_resolve_data, m._ref_resolve_offsets, j)
            result[role] = SNodeRef(
                model_uuid if model_uuid else None,
                node_uuid if node_uuid else None,
                resolve if resolve else None,
            )
        return result

    @property
    def children(self):
        model = self._model
        result = []
        ci = int(model._np_first_child[self._idx])
        while ci != -1:
            result.append(model._get_node(ci))
            ci = int(model._np_next_sibling[ci])
        return result

    def get_property(self, name):
        # looks up the key index once via the model's dedup table andd then scans only this node's property
        # slice so I think typically 0-3 entries
        m = self._model
        i = self._idx
        key_idx = m._get_prop_key_idx(name)
        if key_idx == -1:
            return None
        start = int(m._prop_start[i])
        end = int(m._prop_start[i + 1])
        for j in range(start, end):
            if int(m._prop_key_idxs[j]) == key_idx:
                return m._read_bytes(m._prop_val_data, m._prop_val_offsets, j)
        return None

    def get_reference(self, name):
        from mpscli.model.SNodeRef import SNodeRef

        m = self._model
        i = self._idx
        key_idx = m._get_ref_key_idx(name)
        if key_idx == -1:
            raise KeyError(name)
        start = int(m._ref_start[i])
        end = int(m._ref_start[i + 1])
        for j in range(start, end):
            if int(m._ref_key_idxs[j]) == key_idx:
                model_uuid = m._ref_model_uuids[int(m._ref_model_idxs[j])]
                node_uuid = m._read_bytes(
                    m._ref_node_uuid_data, m._ref_node_uuid_offsets, j
                )
                resolve = m._read_bytes(m._ref_resolve_data, m._ref_resolve_offsets, j)
                return SNodeRef(
                    model_uuid if model_uuid else None,
                    node_uuid if node_uuid else None,
                    resolve if resolve else None,
                )
        raise KeyError(name)

    def get_children(self, role):
        return [c for c in self.children if c.role_in_parent == role]

    def get_descendants(self):
        res = []
        self._collect_descendants(res)
        return res

    def _collect_descendants(self, res):
        for child in self.children:
            res.append(child)
            child._collect_descendants(res)
