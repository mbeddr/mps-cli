package org.mps_cli.model

class SRepository {
    def String name
    def List<SSolution> solutions = []
    def List<SLanguage> languages = []

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

    List<SNode> nodesOfConcept(String fullyQualifiedConceptName) {
        allNodes().findAll { it.concept.name == fullyQualifiedConceptName}
    }

    List<SNode> nodesOfShortConceptName(String shortConceptName) {
        def ending = "." + shortConceptName
        Set<String> conceptNames = new HashSet<>();
        def res = allNodes().findAll {
            def correctEnding = it.concept != null && it.concept.name.endsWith(ending)
            if (correctEnding) conceptNames.add(it.concept.name)
            correctEnding
        }
        if (conceptNames.size() > 1)
            throw new RuntimeException("Multiple concepts found for $shortConceptName : $conceptNames")
        res
    }

    Set<SConcept> conceptsOfLanguage(String langName) {
        languages.find {it.name == langName}?.concepts
    }

    SConcept findConceptByShortName(String conceptShortName) {
        def ending = "." + conceptShortName
        languages.collectMany {it.concepts }.find { it.name.endsWith(ending) }
    }
}
