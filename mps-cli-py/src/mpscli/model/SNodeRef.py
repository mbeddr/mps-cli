class SNodeRef:
    def __init__(self, model_uuid, node_uuid, resolve_info=None):
        self.model_uuid = model_uuid
        self.node_uuid = node_uuid
        self.resolve_info = resolve_info

    def resolve(self, repo):
        model = repo.get_model_by_uuid(self.model_uuid)
        if model is None:
            return None
        return model.get_node_by_uuid(self.node_uuid)
