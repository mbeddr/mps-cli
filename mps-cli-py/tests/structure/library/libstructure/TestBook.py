from tests.structure.library.libstructure.TestLibraryEntityBase import TestLibraryEntityBase
from tests.structure.library.personsstructure.TestPersonRef import TestPersonRef


class TestBook(TestLibraryEntityBase):

    def publicationDate(self) -> int:
        return int(self.get_property("publicationDate"))

    def authors(self) -> list[TestPersonRef]:
        return self.get_children("authors")


