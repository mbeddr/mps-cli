import os
from typing import Set

from mpscli.structuregen.gen.ConceptDeclarationTemplateHelper import create_helper_by_declaration_name
from mpscli.structuregen.gen.EnumDeclarationTemplateHelper import EnumDeclarationTemplateHelper
from mpscli.structuregen.gen.GenerationConstants import ENUM_DECLARATION_CONCEPT_NAME, INTERFACE_DECLARATION_CONCEPT_NAME, CONCEPT_DECLARATION_CONCEPT_NAME, BASE_CONCEPT_FQN
from mpscli.structuregen.gen.StructureGenUtil import get_concept_fqn
from mpscli.structuregen.model.builder.SLanguageStructureRepositoryBuilder import SLanguageStructureRepositoryBuilder
from timeit import default_timer as timer


class StructureFromLanguageGenerator:

    def __init__(self, language_folders, concept_names_to_generate: Set[str], output_folder):
        self.language_folders = language_folders
        self.concept_names_to_generate = concept_names_to_generate
        self.output_folder = output_folder
        self.already_created_concepts = set()
        self.name_to_concept_declaration = {}
        self.snode_to_model_map = {}
        self.lang_repo = None
        self.folder_with_init_py = set()

    def generate_classes(self):
        start = timer()
        lang_repo_builder = SLanguageStructureRepositoryBuilder()
        self.lang_repo = lang_repo_builder.build_from_multiple_path(self.language_folders)
        stop_repo_build = timer()
        self.create_concept_declaration_dicts()
        # ensure that base concept is the first concept to be generated:
        self.create_concept_class(BASE_CONCEPT_FQN)
        if not self.concept_names_to_generate:
            self.concept_names_to_generate = set()
            for concept_declaration in self.lang_repo.get_nodes_of_concept(CONCEPT_DECLARATION_CONCEPT_NAME):
                fqn = get_concept_fqn(concept_declaration, self.snode_to_model_map)
                self.concept_names_to_generate.add(fqn)
        for name_of_concept in self.concept_names_to_generate:
            self.create_concept_class(name_of_concept)

        stop_all = timer()
        duration_repo_build = stop_repo_build - start
        duration_generation = stop_all - stop_repo_build
        overall_duration = stop_all - start
        print(f'''
        Created {len(self.already_created_concepts)} classes in {overall_duration} s (used {duration_repo_build} s for building the repo and {duration_generation} s for the generation.)
        Repo statistics:
            Found: {len(self.lang_repo.get_nodes_of_concept(CONCEPT_DECLARATION_CONCEPT_NAME))} concept declarations
            Found: {len(self.lang_repo.get_nodes_of_concept(INTERFACE_DECLARATION_CONCEPT_NAME))} interface declarations
            Found: {len(self.lang_repo.get_concepts())} concepts in repo
            
            Generation target folder {self.output_folder}
        ''')

        return len(self.already_created_concepts)


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
            print(f"Can not generate concept with name '{concept_name}' as its definition has not been found in the language folder")
            return
        if concept_to_generate in self.already_created_concepts:
            return
        self.already_created_concepts.add(concept_to_generate)
        concept_to_gen_name = concept_to_generate.concept.name
        if concept_to_gen_name == CONCEPT_DECLARATION_CONCEPT_NAME or concept_to_gen_name == INTERFACE_DECLARATION_CONCEPT_NAME:
            concept_declaration_helper = create_helper_by_declaration_name(concept_to_gen_name, concept_to_generate, self.snode_to_model_map, self.lang_repo)
            self.write_to_file(concept_declaration_helper.get_concept_file_path() + ".py", concept_declaration_helper.generate_class())
            self.write_to_file(concept_declaration_helper.get_concept_file_path() + "Impl.py", concept_declaration_helper.generate_class_impl())
            self.write_init_file(concept_declaration_helper.get_concept_folder_path())
            for base in concept_declaration_helper.get_used_classes(True):
                concept_name = get_concept_fqn(base, self.snode_to_model_map)
                self.create_concept_class(concept_name)
        elif concept_to_gen_name == ENUM_DECLARATION_CONCEPT_NAME:
            enum_declaration_helper = EnumDeclarationTemplateHelper(concept_to_generate, self.snode_to_model_map)
            self.write_to_file(enum_declaration_helper.get_concept_file_path() + ".py", enum_declaration_helper.generate_enum_class())
            self.write_init_file(enum_declaration_helper.get_concept_folder_path())
        else:
            print(f"ERROR: Can not concept of type {concept_to_gen_name} as it is an unknown definition")

    def write_to_file(self, path, content):
        file_path = self.output_folder + "/" + path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            if content is not None:
                file.write(content)

    def write_init_file(self, folder):
        if folder in self.folder_with_init_py:
            return
        self.write_to_file(folder + "/" + "__init__.py", None)
        self.folder_with_init_py.add(folder)
