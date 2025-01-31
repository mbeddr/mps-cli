package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.Internal
import org.gradle.api.tasks.TaskAction
import org.mps_cli.cone_of_influence.EntityDependenciesBuilder
import org.mps_cli.model.SModel
import org.mps_cli.model.builder.BuildingDepthEnum
import org.mps_cli.model.builder.SModulesRepositoryBuilder

class ModelDependenciesBuilderTask extends DefaultTask {

    @Input
    List<String> sourcesDir;

    @Internal
    Map<SModel, Set<SModel>> model2AllUpstreamDependencies = [:];

    @Internal
    Map<SModel, Set<SModel>> model2AllDownstreamDependencies = [:];

    ModelDependenciesBuilderTask() {
        group = "MPS-CLI"
        description = "build the upstream/downstream dependencies for all models based on MPS files from 'sourceDir' list"
    }

    @TaskAction
    def buildModelDependencies() {
        def builder = new SModulesRepositoryBuilder(buildingStrategy: BuildingDepthEnum.MODEL_DEPENDENCIES_ONLY)
        def repository = builder.buildAll(sourcesDir)

        (model2AllUpstreamDependencies, model2AllDownstreamDependencies) =
                EntityDependenciesBuilder.buildModelDependencies(repository)
    }
}
