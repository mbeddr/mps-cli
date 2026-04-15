import unittest

from mpscli.model.builder.SModelBuilderBinaryPersistency import (
    SModelBuilderBinaryPersistency,
)

MPB = (
    "../mps_test_projects/"
    "mps_cli_binary_persistency_generated_low_level_access_test_data/"
    "mps.cli.lanuse.library_top.binary_persistency.authors_top.mpb"
)


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.builder = SModelBuilderBinaryPersistency()
        self.builder.build(MPB)

    def test_person_concept_present(self):
        names = [c.name for c in self.builder.index_2_concept.values()]
        self.assertIn("mps.cli.landefs.people.structure.Person", names)

    def test_persons_container_concept_present(self):
        names = [c.name for c in self.builder.index_2_concept.values()]
        self.assertIn("mps.cli.landefs.people.structure.PersonsContainer", names)

    def test_inamed_concept_present(self):
        names = [c.name for c in self.builder.index_2_concept.values()]
        self.assertIn("jetbrains.mps.lang.core.structure.INamedConcept", names)

    def test_concept_id_map_consistent_with_index_map(self):
        for concept in self.builder.index_2_concept.values():
            self.assertIn(
                concept.uuid,
                self.builder.concept_id_2_concept,
                f"Concept {concept.name!r} missing from concept_id_2_concept",
            )

    def test_known_properties_populated(self):
        prop_names = list(self.builder.index_2_property.values())
        self.assertIn(
            "name",
            prop_names,
            "Expected 'name' property from INamedConcept in authors_top.mpb",
        )

    def test_known_child_role_populated(self):
        child_roles = list(self.builder.index_2_child_role_in_parent.values())
        self.assertIn(
            "persons",
            child_roles,
            "Expected 'persons' child role from PersonsContainer in authors_top.mpb",
        )
