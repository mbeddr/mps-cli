package org.mps_cli.gradle.plugin


import org.gradle.api.tasks.Internal
import org.gradle.api.tasks.TaskAction
import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SSolutionModule
import org.mps_cli.model.builder.BuildingDepthEnum
import org.mps_cli.model.builder.SModulesRepositoryBuilder

class ModuleDependenciesBuilderTask extends AbstractDependenciesBuilderTask {

    @Internal
    Map<SModuleBase, Set<SModuleBase>> module2AllUpstreamDependencies = [:];

    @Internal
    Map<SModuleBase, Set<SModuleBase>> module2AllDownstreamDependencies = [:];

    ModuleDependenciesBuilderTask() {
        group("MPS-CLI")
        description("build the upstream/downstream dependencies for all modules based on MPS files from 'sourceDir' list")
    }

    @TaskAction
    def buildModuleDependencies() {
        builder = new SModulesRepositoryBuilder(buildingStrategy: BuildingDepthEnum.MODULE_DEPENDENCIES_ONLY)
        buildEntityDependencies(module2AllUpstreamDependencies, module2AllDownstreamDependencies)
    }

    @Override
    List<Object> allEntities() {
        repository.modules
    }

    @Override
    List<Object> directDependencies(Object entity) {
        ((SSolutionModule)entity).dependencies;
    }
}