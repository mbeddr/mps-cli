package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.Internal
import org.gradle.api.tasks.TaskAction
import org.mps_cli.model.SRepository
import org.mps_cli.model.SSolution
import org.mps_cli.model.builder.BuildingDepthEnum
import org.mps_cli.model.builder.SLanguageBuilder
import org.mps_cli.model.builder.SSolutionsRepositoryBuilder

class ModuleDependenciesBuilderTask extends AbstractDependenciesBuilderTask {

    @Internal
    Map<SSolution, Set<SSolution>> solution2AllUpstreamDependencies = [:];

    @Internal
    Map<SSolution, Set<SSolution>> solution2AllDownstreamDependencies = [:];

    ModuleDependenciesBuilderTask() {
        group("MPS-CLI")
        description("build the upstream/downstream dependencies for all solutions based on MPS files from 'sourceDir' list")
    }

    @TaskAction
    def buildModuleDependencies() {
        builder = new SSolutionsRepositoryBuilder(buildingStrategy: BuildingDepthEnum.MODULE_DEPENDENCIES_ONLY)
        buildEntityDependencies(solution2AllUpstreamDependencies, solution2AllDownstreamDependencies)
    }

    @Override
    List<Object> allEntities() {
        builder.repo.solutions
    }

    @Override
    List<Object> directDependencies(Object entity) {
        ((SSolution)entity).dependencies;
    }
}