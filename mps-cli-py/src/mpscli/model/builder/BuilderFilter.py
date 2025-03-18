
class BuilderFilter:
    """
    The BuilderFilter can be used to define whether a given module, model or root shall be build or not.
    If the respective method returns true the element is included. Otherwise, it is excluded from the build
    Note: the build root only has an affect if file per root persistency is used.

    """
    def build_module(self, module_file_path):
        return True

    def build_model(self, model_file_path):
        return True

    def build_root(self, root_file_path):
        return True