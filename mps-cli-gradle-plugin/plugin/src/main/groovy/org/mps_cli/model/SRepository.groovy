package org.mps_cli.model

class SRepository {
    List<SModuleBase> modules = []
    List<SLanguage> languages = []

    private List<SModel> allModelsCache = null
    private List<SNode> allNodesCache = null
    private Map<String, SModel> id2modelsCache = null
    private Map<String, SModuleBase> id2ModulesCache = null

    List<SModel> allModels() {
        if (allModelsCache == null) {
            allModelsCache = modules.collectMany { it.models }
        }
        allModelsCache
    }

    List<SNode> allNodes() {
        if (allNodesCache == null) {
            allNodesCache = allModels().collectMany { it.allNodes }
        }
        allNodesCache
    }

    Map<String, SModel> id2models() {
        if (id2modelsCache == null) {
            id2modelsCache = allModels().collectEntries {[it.modelId, it] }
        }
        id2modelsCache
    }

    Map<String, SModuleBase> id2modules() {
        if (id2ModulesCache == null) {
            id2ModulesCache = modules.collectEntries {[it.moduleId, it] }
        }
        id2ModulesCache
    }

    List<SModel> findModelByName(String modelName) {
        allModels().findAll { (it.name == modelName) }
    }

    SModel findModelByRealPath(String realPath) {
        if (realPath == null) return null
        allModels().find { (it.pathToModelFile == realPath) }
    }

    SModuleBase findModuleByRealPath(String realPath) {
        if (realPath == null) return null
        modules.find { (it.pathToModuleFile == realPath) }
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

    SModuleBase findModuleByName(String moduleName) {
        modules.find {it.name.equals(moduleName) }
    }
}
