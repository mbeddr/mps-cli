
class SConcept:

    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid
        self.properties = {}
        self.children = {}
        self.references = {}