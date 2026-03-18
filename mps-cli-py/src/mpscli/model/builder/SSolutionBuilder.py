import os
import xml.etree.ElementTree as ET
from pathlib import Path

from mpscli.model.SSolution import SSolution
from mpscli.model.builder.SModelBuilderDefaultPersistency import (
    SModelBuilderDefaultPersistency,
)
from mpscli.model.builder.SModelBuilderFilePerRootPersistency import (
    SModelBuilderFilePerRootPersistency,
)
from mpscli.model.builder.SModelBuilderBinaryPersistency import (
    SModelBuilderBinaryPersistency,
)


class SSolutionBuilder:
    def build_solution(self, path_to_msd_file):
        solution = self.extract_solution_core_info(path_to_msd_file)
        path_to_solution_dir = path_to_msd_file.parent
        solution.path_to_solution_file = path_to_msd_file

        print("building from:", path_to_solution_dir)

        path_to_models_dir = path_to_solution_dir / "models"

        if not path_to_models_dir.exists():
            print(
                "ERROR: 'models' directory not found! No model is loaded from path: "
                + str(path_to_solution_dir)
            )
            return None

        for model_path in Path(path_to_models_dir).rglob("*"):

            if model_path.is_file() and model_path.suffix == ".mpb":
                builder = SModelBuilderBinaryPersistency()
                model = builder.build(model_path)
                solution.models.append(model)
                continue

            if model_path.is_dir() and (model_path / ".model").exists():
                builder = SModelBuilderFilePerRootPersistency()
                model = builder.build(model_path)
                solution.models.append(model)
                continue

            if model_path.is_file() and model_path.suffix == ".mps":
                builder = SModelBuilderDefaultPersistency()
                model = builder.build(model_path)
                solution.models.append(model)

        return solution

    def extract_solution_core_info(self, solution_file):
        tree = ET.parse(solution_file)
        solution_xml_node = tree.getroot()
        solution_name = solution_xml_node.get("name")
        solution_uuid = solution_xml_node.get("uuid")
        solution = SSolution(solution_name, solution_uuid)
        return solution
