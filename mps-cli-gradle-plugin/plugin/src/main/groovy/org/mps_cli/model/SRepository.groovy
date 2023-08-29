package org.mps_cli.model

class SRepository {

    private List<SModuleBase> modules;
    private List<SLanguage> languages;

    private List<SModel> models;
    private List<SNode> nodes;
    private Map<String, SModel> id2modelsCache;
    private Map<String, SModuleBase> id2ModulesCache;

    SRepository(List<SModuleBase> modules, List<SLanguage> languages) {
        this.modules = modules.asImmutable()
        this.languages = languages.asImmutable()

        this.models = modules.collectMany { it.models }.asImmutable()
        this.nodes = models.collectMany { it.allNodes }.asImmutable()
        this.id2modelsCache = models.collectEntries { [it.modelId, it] }.asImmutable()
        this.id2ModulesCache = modules.collectEntries { [it.moduleId, it] }.asImmutable()
    }

    List<SModuleBase> getModules() { modules }

    List<SLanguage> getLanguages() { languages }

    List<SModel> allModels() { models }

    List<SNode> allNodes() { nodes }

    Map<String, SModel> id2models() { id2modelsCache }

    Map<String, SModuleBase> id2modules() { id2ModulesCache }

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
        allNodes().findAll { it.concept.name == fullyQualifiedConceptName }
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
        languages.find { it.name == langName }?.concepts
    }

    SConcept findConceptByShortName(String conceptShortName) {
        def ending = "." + conceptShortName
        languages.collectMany { it.concepts }.find { it.name.endsWith(ending) }
    }

    SModuleBase findModuleByName(String moduleName) {
        modules.find { it.name.equals(moduleName) }
    }
}
