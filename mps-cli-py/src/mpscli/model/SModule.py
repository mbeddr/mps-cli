class SModule:
    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid
        self.models = []
        self.path_to_module_file = ""
