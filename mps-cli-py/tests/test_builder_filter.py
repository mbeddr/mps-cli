import unittest

from mpscli.model.builder.BuilderFilter import BuilderFilter
from tests.test_base import TestBase
from parameterized import parameterized


class PersonFilePerRootFilter(BuilderFilter):
    def build_root(self, root_file_path):
        with open(root_file_path, 'r') as root:
            for line in root:
                if "Person" in line:
                    return False
        return True

class TestBuilderFilter(TestBase):


    @parameterized.expand(['mps_cli_lanuse_file_per_root'])
    def test_languages_and_concepts(self, test_data_location):
        # given the person file filter:
        person_file_filter = PersonFilePerRootFilter()

         # when the setup has been executed with the filter
        self.doSetUp(test_data_location, person_file_filter)

        # then no persons should have been extracted
        people_lan_name = "mps.cli.landefs.people"
        people = self.repo.get_nodes_of_concept(people_lan_name)
        self.assertIsNone(people, f"Did not expect any people instances, as the language should be ignroed, but found {len(people_lan_name)} in repo")
        landefs_people = self.repo.find_language_by_name(people_lan_name)
        self.assertIsNone(landefs_people, f"Did not expect that language {people_lan_name} in repo")


if __name__ == '__main__':
    unittest.main()
