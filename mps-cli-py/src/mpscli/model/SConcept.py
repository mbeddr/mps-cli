import logging

_log = logging.getLogger(__name__)


class SConcept:

    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid
        self.properties = []
        self.children = []
        self.references = []

    def print_concept_details(self):
        _log.debug("concept: %s", self.name)
        _log.debug("\tproperties: ")
        for property in self.properties:
            _log.debug("\t\t%s", property)
        _log.debug("\tchildren: ")
        for child in self.children:
            _log.debug("\t\t%s", child)
        _log.debug("\treferences: ")
        for reference in self.references:
            _log.debug("\t\t%s", reference)
        _log.debug("<<<")
