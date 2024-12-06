import mpscli


class SNodeClassFinder:
    def get_snode_class(self, concept_name):
        return getattr(mpscli, "SNode")
