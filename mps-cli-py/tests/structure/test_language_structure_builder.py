import unittest

from mpscli.structuregen.model.builder.SLanguageStructureRepositoryBuilder import SLanguageStructureRepositoryBuilder


class TestLanguageBuilder(unittest.TestCase):

    def test_building_languages(self):
        # given: the path to language definition
        path = "../../../mps_test_projects/mps_cli_landefs"

        # when: the repo has been build
        repo = TestLanguageBuilder.create_language_repo(path)

        # then: we should have nodes, and nodes of types ConceptDeclaration with correct content
        print(f"Found {len(repo.get_nodes())} nodes")
        self.assertTrue(len(repo.get_nodes()) > 10, f"At least 10 nodes are expected in the repo. Found only {len(repo.get_nodes())}")
        self.assertTrue(len(repo.get_concepts()) > 6, f"At least 10 concepts expected in the repo. Found only {len(repo.get_concepts())}")
        self.ensure_minimal_number_of_instances(repo, "jetbrains.mps.lang.structure.structure.PropertyDeclaration", 2)
        self.ensure_minimal_number_of_instances(repo, "jetbrains.mps.lang.structure.structure.ConceptDeclaration", 3)
        self.ensure_minimal_number_of_instances(repo, "jetbrains.mps.lang.structure.structure.LinkDeclaration", 2)

    @staticmethod
    def create_language_repo(path):
        language_builder = SLanguageStructureRepositoryBuilder()

        repo = language_builder.build(path)
        return repo

    def ensure_minimal_number_of_instances(self, repo, concept_name, minimal_concept_occurrence):
        nodes_of_concept = repo.get_nodes_of_concept(concept_name)
        self.assertTrue(len(nodes_of_concept) > minimal_concept_occurrence,
                        f"Found only {len(nodes_of_concept)} instances of concept {concept_name}. Expected at least {minimal_concept_occurrence} instances.")


if __name__ == '__main__':
    unittest.main()