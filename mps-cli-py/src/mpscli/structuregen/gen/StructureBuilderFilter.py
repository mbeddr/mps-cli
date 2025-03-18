from mpscli.model.builder.BuilderFilter import BuilderFilter


class StructureBuilderFilter(BuilderFilter):

    def build_model(self, model_file):
        return str(model_file).endswith("structure.mps")