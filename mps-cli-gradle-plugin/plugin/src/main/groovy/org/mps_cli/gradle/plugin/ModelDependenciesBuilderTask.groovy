package org.mps_cli.gradle.plugin


import org.gradle.api.tasks.Internal
import org.gradle.api.tasks.TaskAction
import org.mps_cli.model.SModel
import org.mps_cli.model.SSolution
import org.mps_cli.model.builder.BuildingDepthEnum
import org.mps_cli.model.builder.SSolutionsRepositoryBuilder

class ModelDependenciesBuilderTask extends AbstractDependenciesBuilderTask {

    @Internal
    Map<SModel, Set<SModel>> model2AllUpstreamDependencies = [:];

    @Internal
    Map<SModel, Set<SModel>> model2AllDownstreamDependencies = [:];

    ModelDependenciesBuilderTask() {
        group("MPS-CLI")
        description("build the upstream/downstream dependencies for all models based on MPS files from 'sourceDir' list")
    }

    @TaskAction
    def buildModelDependencies() {
        builder = new SSolutionsRepositoryBuilder(buildingStrategy: BuildingDepthEnum.MODEL_DEPENDENCIES_ONLY)
        buildEntityDependencies(model2AllUpstreamDependencies, model2AllDownstreamDependencies)
    }

    @Override
    List<Object> allEntities() {
        builder.repo.allModels()
    }

    @Override
    List<Object> directDependencies(Object entity) {
        ((SModel)entity).imports;
    }
}