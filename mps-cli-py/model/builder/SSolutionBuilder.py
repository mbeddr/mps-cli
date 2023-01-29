
import xml.etree.ElementTree as ET
from model.SSolution import SSolution
from model.builder.SModelBuilderFilePerRootPersistency import SModelBuilderFilePerRootPersistency


class SSolutionBuilder:

    def build_solution(self, path_to_msd_file):
        solution = self.extract_solution_core_info(path_to_msd_file)
        path_to_solution_dir = path_to_msd_file.parent
        print("building from:", path_to_solution_dir)
        path_to_models_dir = path_to_solution_dir / 'models'

        for path_to_model in path_to_models_dir.iterdir():
            if path_to_model.is_dir():
                file_per_root_builder = SModelBuilderFilePerRootPersistency()
                model = file_per_root_builder.build(path_to_model)
                solution.models.append(model)

        return solution

    def extract_solution_core_info(self, solution_file):
        tree = ET.parse(solution_file)
        solution_xml_node = tree.getroot()
        solution_name = solution_xml_node.get("name")
        solution_uuid = solution_xml_node.get("uuid")
        solution = SSolution(solution_name, solution_uuid)
        return solution
