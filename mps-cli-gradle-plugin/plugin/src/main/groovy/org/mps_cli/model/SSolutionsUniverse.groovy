package org.mps_cli.model

class SSolutionsUniverse {
    def String name
    def List<SSolution> solutions = []


    def allNodes = {
        def nodes = []
        solutions.each { sol ->
            sol.models.each {mod ->
                nodes.addAll(mod.allNodes)
            }
        }
        nodes
    }.memoize()

    def nodesWithConcept(conceptName) {
        allNodes().findAll { it.concept != null && it.concept.endsWith("." + conceptName)}
    }
}
