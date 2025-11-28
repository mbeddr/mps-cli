import logging
import os
from pathlib import Path

from mpscli.model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder
from mpscli.structuregen.gen.ConceptDeclarationTemplateHelper import create_helper_by_declaration_name
from mpscli.structuregen.gen.EnumDeclarationTemplateHelper import EnumDeclarationTemplateHelper
from mpscli.structuregen.gen.GenerationConstants import ENUM_DECLARATION_CONCEPT_NAME, INTERFACE_DECLARATION_CONCEPT_NAME, CONCEPT_DECLARATION_CONCEPT_NAME, BASE_CONCEPT_FQN
from mpscli.structuregen.gen.StructureBuilderFilter import StructureBuilderFilter
from mpscli.structuregen.gen.StructureGenUtil import get_concept_fqn
from mpscli.structuregen.model.builder.SLanguageStructureRepositoryBuilder import SLanguageStructureRepositoryBuilder
from timeit import default_timer as timer



class StructureFromLanguageGenerator:

    class GenerationMode:
        GENERATE_ALL = "GENERATE_ALL"
        GENERATE_CONCEPTS = "GENERATE_CONCEPTS"
        GENERATE_CONCEPTS_IN_LANGUAGE_FOLDERS = "GENERATE_CONCEPTS_IN_LANGUAGE_FOLDERS"
        GENERATE_CONCEPTS_AND_IN_LANGUAGE_FOLDERS = "GENERATE_CONCEPTS_AND_IN_LANGUAGE_FOLDERS"
        GENERATE_CONCEPTS_USED_IN_PROJECTS = "GENERATE_CONCEPTS_USED_IN_PROJECTS"

        def __init__(self, gen_mode, concepts_to_generate, folders_to_generate, generate_concepts_in_solutions):
            self.gen_mode = gen_mode
            self.concepts_to_generate = concepts_to_generate
            self.folders_to_generate = folders_to_generate
            self.generate_concepts_in_solutions = generate_concepts_in_solutions

    def __init__(self, language_folders, generate_mode: GenerationMode, output_folder):
        self.language_folders = language_folders
        self.generation_mode = generate_mode
        self.output_folder = output_folder
        self.already_created_concepts = set()
        self.name_to_concept_declaration = {}
        self.snode_to_model_map = {}
        self.lang_repo = None
        self.folder_with_init_py = set()

    @classmethod
    def init_generate_all(cls, language_folders, output_folder):
        return cls(language_folders, cls.GenerationMode(StructureFromLanguageGenerator.GenerationMode.GENERATE_ALL, None, None, None), output_folder)
    
    @classmethod
    def init_generate_concepts(cls, language_folders, concepts_to_generate, output_folder):
        mode_for_concepts = cls.GenerationMode(StructureFromLanguageGenerator.GenerationMode.GENERATE_CONCEPTS, concepts_to_generate, None, None)
        return cls(language_folders, mode_for_concepts, output_folder)

    @classmethod
    def init_generate_concepts_from_folder(cls, language_folders_to_generate, additional_language_folders, output_folder):
        mode_for_folder = cls.GenerationMode(StructureFromLanguageGenerator.GenerationMode.GENERATE_CONCEPTS_IN_LANGUAGE_FOLDERS, None, language_folders_to_generate, None)
        all_language_folders = language_folders_to_generate + additional_language_folders
        return cls(all_language_folders, mode_for_folder, output_folder)

    @classmethod
    def init_generate_concepts_and_folder(cls, concepts_to_generate, language_folders_to_generate, additional_language_folders, output_folder):
        gen_mode = cls.GenerationMode(StructureFromLanguageGenerator.GenerationMode.GENERATE_CONCEPTS_AND_IN_LANGUAGE_FOLDERS, concepts_to_generate, language_folders_to_generate, None)
        all_language_folders = language_folders_to_generate + additional_language_folders
        return cls(all_language_folders, gen_mode, output_folder)

    @classmethod
    def init_generate_concepts_used_in_projects(cls, language_folders, project_folders, output_folder):
        gen_mode = cls.GenerationMode(StructureFromLanguageGenerator.GenerationMode.GENERATE_CONCEPTS_USED_IN_PROJECTS, None,
                                             language_folders, project_folders)
        return cls(language_folders, gen_mode, output_folder)

    def generate_classes(self):
        start = timer()
        lang_repo_builder = SLanguageStructureRepositoryBuilder(None, StructureBuilderFilter())
        self.lang_repo = lang_repo_builder.build_from_multiple_path(self.language_folders)
        stop_repo_build = timer()

        self.create_concept_declaration_dicts()
        concepts_to_generate = self.get_concepts_to_generate()

        # ensure that base concept is the first concept to be generated:
        self.create_concept_class(BASE_CONCEPT_FQN)
        for name_of_concept in concepts_to_generate:
            self.create_concept_class(name_of_concept)

        stop_all = timer()
        duration_repo_build = stop_repo_build - start
        duration_generation = stop_all - stop_repo_build
        overall_duration = stop_all - start
        logging.info(f'''
        Created {len(self.already_created_concepts)} classes in {overall_duration} s (used {duration_repo_build} s for building the repo and {duration_generation} s for the generation.)
        Repo statistics:
            Found: {len(self.lang_repo.get_nodes_of_concept(CONCEPT_DECLARATION_CONCEPT_NAME))} concept declarations
            Found: {len(self.lang_repo.get_nodes_of_concept(INTERFACE_DECLARATION_CONCEPT_NAME))} interface declarations
            Found: {len(self.lang_repo.get_concepts())} concepts in repo
            
            Generation target folder {self.output_folder}
        ''')

        return len(self.already_created_concepts)

    def get_concepts_to_generate(self):
        if self.generation_mode.gen_mode == self.GenerationMode.GENERATE_CONCEPTS:
            return self.generation_mode.concepts_to_generate
        if self.generation_mode.gen_mode == self.GenerationMode.GENERATE_ALL:
            concepts_to_generate = self.lang_repo.get_nodes_of_concept(CONCEPT_DECLARATION_CONCEPT_NAME)
            return self.concepts_to_concepts_fqn(concepts_to_generate )
        if self.generation_mode.gen_mode == self.GenerationMode.GENERATE_CONCEPTS_USED_IN_PROJECTS:
            builder = SSolutionsRepositoryBuilder()
            repo = builder.build_from_multiple_path(self.generation_mode.generate_concepts_in_solutions)
            concepts_to_generate = set()
            concepts_to_generate.update([concept.name for concept in repo.get_concepts()])
            return concepts_to_generate
        concept_names_to_generate = []
        if self.generation_mode.gen_mode == self.GenerationMode.GENERATE_CONCEPTS_AND_IN_LANGUAGE_FOLDERS:
            # in case of concept and folders, add the concepts
            concept_names_to_generate.extend(self.generation_mode.concepts_to_generate)
        concepts_to_generate = []
        for solution in self.lang_repo.solutions:
            module_path = os.path.abspath(solution.path_to_module_file)
            paths_to_generate = [os.path.abspath(dir_path) for dir_path in self.generation_mode.folders_to_generate]
            for path_to_generate in paths_to_generate:
                if os.path.commonpath([module_path, path_to_generate]) == path_to_generate:
                    for model in solution.models:
                        concept_declarations = [cd for cd in model.root_nodes if cd.concept.name == CONCEPT_DECLARATION_CONCEPT_NAME]
                        concepts_to_generate.extend(concept_declarations)
        concept_names_to_generate.extend(self.concepts_to_concepts_fqn(concepts_to_generate))
        if not concept_names_to_generate:
            logging.error("No concepts for generation found")
        return concept_names_to_generate

    def concepts_to_concepts_fqn(self, concepts):
        concepts_fqn = [get_concept_fqn(concept_declaration, self.snode_to_model_map) for concept_declaration in concepts ]
        return concepts_fqn

    def create_concept_declaration_dicts(self):
        for solution in self.lang_repo.solutions:
            for model in solution.models:
                for root in model.root_nodes:
                    if (root.concept.name == CONCEPT_DECLARATION_CONCEPT_NAME or root.concept.name == INTERFACE_DECLARATION_CONCEPT_NAME or
                            root.concept.name == ENUM_DECLARATION_CONCEPT_NAME):
                        fqn = model.name + "." + root.get_property("name")
                        self.snode_to_model_map[root] = model
                        self.name_to_concept_declaration[fqn] = root

    def create_concept_class(self, concept_name):
        concept_to_generate = self.name_to_concept_declaration.get(concept_name)
        if concept_to_generate is None:
            logging.error(f"Can not generate concept with name '{concept_name}' as its definition has not been found in the language folder")
            return
        if concept_to_generate in self.already_created_concepts:
            return
        self.already_created_concepts.add(concept_to_generate)
        concept_to_gen_name = concept_to_generate.concept.name
        if concept_to_gen_name == CONCEPT_DECLARATION_CONCEPT_NAME or concept_to_gen_name == INTERFACE_DECLARATION_CONCEPT_NAME:
            concept_declaration_helper = create_helper_by_declaration_name(concept_to_gen_name, concept_to_generate, self.snode_to_model_map, self.lang_repo)
            self.write_to_file(concept_declaration_helper.get_concept_file_path() + ".py", concept_declaration_helper.generate_class())
            self.write_to_file(concept_declaration_helper.get_concept_file_path() + "Impl.py", concept_declaration_helper.generate_class_impl())
            self.write_init_file_in_folder_and_parents(concept_declaration_helper.get_concept_folder_path())
            for base in concept_declaration_helper.get_used_classes(True):
                concept_name = get_concept_fqn(base, self.snode_to_model_map)
                self.create_concept_class(concept_name)
        elif concept_to_gen_name == ENUM_DECLARATION_CONCEPT_NAME:
            enum_declaration_helper = EnumDeclarationTemplateHelper(concept_to_generate, self.snode_to_model_map)
            self.write_to_file(enum_declaration_helper.get_concept_file_path() + ".py", enum_declaration_helper.generate_enum_class())
            self.write_init_file_in_folder_and_parents(enum_declaration_helper.get_concept_folder_path())
        else:
            logging.error(f"Can not get concept of type {concept_to_gen_name} as it is an unknown definition")

    def write_to_file(self, path, content):
        file_path = self.output_folder + "/" + path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            if content is not None:
                file.write(content)

    def write_init_file_in_folder_and_parents(self, folder):
        if folder in self.folder_with_init_py or folder == "." or folder is None:
            return
        self.write_to_file(folder + "/" + "__init__.py", None)
        self.folder_with_init_py.add(folder)
        parent_path = Path(folder).parent
        self.write_init_file_in_folder_and_parents(str(parent_path))
