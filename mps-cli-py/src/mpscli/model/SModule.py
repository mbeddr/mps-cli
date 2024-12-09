class SModule:
    def __init__(self, name, uuid, module_model_folder):
        self.name = name
        self.uuid = uuid
        self.models = []
        self.path_to_module_file = ""
        self.module_model_folder = module_model_folder
