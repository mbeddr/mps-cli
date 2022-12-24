package org.mps_cli.model

class SConcept {
    String name
    Set<SConcept> superConcepts = new HashSet<>()
    Set<String> properties = new HashSet<>()
    Set<String> children = new HashSet<>()
    Set<String> references = new HashSet<>()

    String getShortName() {
        name.substring(name.lastIndexOf(".") + 1)
    }
}
