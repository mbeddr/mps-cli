package org.mps_cli.model

class SRepository {
    def String name
    def List<SSolution> solutions = []


    List<SModel> allModels() {
        def models = []
        solutions.each { sol ->
            models.addAll(sol.models)
        }
        models
    }

    Map<String, SModel> id2models() {
        allModels().collectEntries {[it.modelId, it]}
    }

    List<SNode> allNodes() {
        def nodes = []
        allModels().each { mod ->
            nodes.addAll(mod.allNodes)
        }
        nodes
    }

    def nodesWithConcept(conceptName) {
        allNodes().findAll { it.concept != null && it.concept.endsWith("." + conceptName)}
    }
}
