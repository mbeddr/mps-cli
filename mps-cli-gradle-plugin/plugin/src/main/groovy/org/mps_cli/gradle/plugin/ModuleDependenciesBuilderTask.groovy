package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.Internal
import org.gradle.api.tasks.TaskAction
import org.mps_cli.cone_of_influence.EntityDependenciesBuilder
import org.mps_cli.model.SModuleBase
import org.mps_cli.model.builder.BuildingDepthEnum
import org.mps_cli.model.builder.SModulesRepositoryBuilder

class ModuleDependenciesBuilderTask extends DefaultTask {

    @Input
    List<String> sourcesDir;

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
        def builder = new SModulesRepositoryBuilder(buildingStrategy: BuildingDepthEnum.MODULE_DEPENDENCIES_ONLY)
        def repository = builder.buildAll(sourcesDir)

        (module2AllUpstreamDependencies, module2AllDownstreamDependencies) =
                EntityDependenciesBuilder.buildModuleDependencies(repository)
    }
}