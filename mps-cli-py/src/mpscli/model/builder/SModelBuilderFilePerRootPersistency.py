from mpscli.model.builder.SModelBuilderBase import SModelBuilderBase
import xml.etree.ElementTree as ET


class MpsrFileFiler:

    def is_mpsr_file_needed(self, file):
        return True


class SModelBuilderFilePerRootPersistency(SModelBuilderBase):

    def __init__(self, mpsr_file_filter=None):
        if mpsr_file_filter is None:
            self.mpsr_file_filter = MpsrFileFiler()
        else:
            self.mpsr_file_filter = mpsr_file_filter
        super().__init__()

    def build(self, path):
        model_file = path / '.model'
        tree = ET.parse(model_file)
        model_xml_node = tree.getroot()
        model = self.extract_model_core_info(model_xml_node)
        model.path_to_model_file = model_file

        for file in path.iterdir():
            if file.suffix == '.mpsr' and self.mpsr_file_filter.is_mpsr_file_needed(file):
                root_node = self.extract_root_node(model, file)
                model.root_nodes.append(root_node)

        return model

    def extract_root_node(self, model, mpsr_file):
        tree = ET.parse(mpsr_file)
        model_xml_node = tree.getroot()
        self.extract_imports_and_registry(model_xml_node)
        root_node = model_xml_node.find("node")
        return self.extract_node(model, root_node)
