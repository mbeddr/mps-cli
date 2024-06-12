import sys
sys.path.insert(1, '..\..\mps-cli-py\src')

from mpscli.model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder

builder = SSolutionsRepositoryBuilder()
repo = builder.build('..\\..\\mps_test_projects\\mps_cli_lanuse_file_per_root')

print("\n\n##### Incremental Iteration through Models #####")
print("number of parsed solutions: " + str(len(repo.solutions)))
print("parsed solutions, models and root nodes:")
for sol in repo.solutions:
    print("\t" + sol.name)
    for model in sol.models:
        print("\t\t" + model.name)
        for root in model.root_nodes:
            print("\t\t\t" + root.get_property("name"))

print("\n\n##### Incremental Iteration through the Meta-Level #####")
print("all languages and concepts:")
for lan in repo.languages:
    print("\t" + lan.name)
    for concept in lan.concepts:
        print("\t\t" + concept.name)
        for property in concept.properties:
            print("\t\t\t" + property + " (prop)")
        for child in concept.children:
            print("\t\t\t" + child + " (child)")
        for reference in concept.references:
            print("\t\t\t" + reference + " (reference)")

print("\n\n##### Direct Deep Access to Models #####")
print("number of nodes: " + str(len(repo.get_nodes())))
books = repo.get_nodes_of_concept("mps.cli.landefs.library.structure.Book")
print("number of books: " + str(len(books)))
books_names = list(map(lambda b : b.get_property("name"), books))
print("all books: " + str(books_names))

print("\n\n##### Navigate through Nodes #####")
# find out the concept properties, children, references
book_concept = repo.find_concept_by_name("mps.cli.landefs.library.structure.Book")
book_concept.print_concept_details()
five_weeks_in_baloon = next(x for x in books if x.get_property("name") == "Five Weeks in Baloon")
authors = five_weeks_in_baloon.get_children("authors")
print(authors[0].concept.name)
repo.find_concept_by_name("mps.cli.landefs.people.structure.PersonRef").print_concept_details()
print ("The author of 'Five Weeks in Baloon' is '" + authors[0].get_reference("person").resolve(repo).get_property("name") + "'")