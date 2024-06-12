
class SConcept:

    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid
        self.properties = []
        self.children = []
        self.references = []

    def print_concept_details(self):
        print("concept: " + self.name)
        print("\tproperties: ")
        for property in self.properties:
            print("\t\t" + property)
        print("\tchildren: ")
        for child in self.children:
            print("\t\t" + child)
        print("\treferences: ")
        for reference in self.references:
            print("\t\t" + reference)
        print("<<<")