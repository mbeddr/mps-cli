import unittest

from mpscli.model.NodeList import NodeList
from mpscli.model.SModel import SModel
from mpscli.model.SRepository import SRepository
from mpscli.model.SSolution import SSolution
from tests.structure.library.libstructure.TestBookImpl import TestBookImpl
from tests.structure.library.libstructure.TestINamedConcept import TestINamedConcept
from tests.structure.library.libstructure.TestLibraryImpl import TestLibraryImpl


class TestBase(unittest.TestCase):

    def setUp(self):
        library = TestLibraryImpl("TLI1", TestLibraryImpl.get_concept_fqn(), None, None)
        library.name = "TestLib"
        book1 = TestBookImpl("TB1", TestBookImpl.get_concept_fqn(), "entities", library)
        book1.properties["name"] = "TestBook1Name"
        book2 = TestBookImpl("TB2", TestBookImpl.get_concept_fqn(), "entities", library)
        book2.properties["name"] = "TestBook2Name"
        book3 = TestBookImpl("TB3", TestBookImpl.get_concept_fqn(), "entities", library)
        book3.properties["name"] = "TestBook3Name"
        library.children.append(book1)
        library.children.append(book2)
        library.children.append(book3)

        model = SModel("TestModel", "123", True)
        model.root_nodes.append(library)
        solution = SSolution("TestSolution", "456", "")
        solution.models.append(model)
        repo = SRepository()
        repo.solutions.append(solution)
        self.repo = repo

    def test_of_concept(self):
        # given: the setup repo
        # when: book concepts should be found
        books = self.repo.get_nodes().of_concept(TestBookImpl)
        named_concepts = self.repo.get_nodes().of_concept(TestINamedConcept)

        #then
        self.assertEqual(3, len(books), "Expected three books")
        self.assertEqual(4, len(named_concepts), "Expected four named elements")

    def test_is_empty(self):
        # given: the setup repo
        # when: book concepts should be found
        books = self.repo.get_nodes().of_concept(TestBookImpl)
        is_empty = books.is_empty()
        is_not_empty = books.is_not_empty()

        # then
        self.assertFalse(is_empty)
        self.assertTrue(is_not_empty)


    def test_where(self):
        # given: the setup repo
        # when: book concepts should be found
        books_filtered = self.repo.get_nodes().of_concept(TestBookImpl).where(lambda b: b.name().startswith("TestBook3"))

        # then
        self.assertEqual(1, len(books_filtered), "Expected one book")

    def test_for_each(self):
        # given: the setup repo
        result_names = []

        # when: book concepts should be found
        self.repo.get_nodes().of_concept(TestBookImpl).for_each(lambda node: result_names.append(node.name()))

        # then
        self.assertEqual(3, len(result_names), "Expected three entries")
        self.assertTrue("TestBook1Name" in result_names)
        self.assertTrue("TestBook2Name" in result_names)
        self.assertTrue("TestBook3Name" in result_names)

    def test_select(self):
        # given: the setup repo
        # when: book concepts should be found
        books_transformed = self.repo.get_nodes().of_concept(TestBookImpl).select(lambda node: node.name())

        # then
        self.assertEqual(3, len(books_transformed), "Expected three entries")
        self.assertTrue("TestBook1Name" in books_transformed)
        self.assertTrue("TestBook2Name" in books_transformed)
        self.assertTrue("TestBook3Name" in books_transformed)

    def test_select_many(self):
        # given: the setup repo
        result_nodes = NodeList()
        result_nodes.append(self.repo.get_nodes().of_concept(TestBookImpl))
        result_nodes.append(self.repo.get_nodes().of_concept(TestBookImpl))
        result_nodes.append(self.repo.get_nodes().of_concept(TestBookImpl))
        result_nodes.append(self.repo.get_nodes().of_concept(TestBookImpl)[0])

        # when: book concepts should be found
        books_transformed = result_nodes.select_many(lambda node: node.name())

        # then
        self.assertEqual(10, len(books_transformed), "Expected three entries")
        self.assertTrue("TestBook1Name" in books_transformed)
        self.assertTrue("TestBook2Name" in books_transformed)
        self.assertTrue("TestBook3Name" in books_transformed)


if __name__ == '__main__':
    unittest.main()