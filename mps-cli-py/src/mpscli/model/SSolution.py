from mpscli.model.SModule import SModule


class SSolution(SModule):

    def __init__(self, name, uuid, module_model_folder):
        super().__init__(name, uuid, module_model_folder)

    def path_to_solution_file(self):
        return self.path_to_module_file
