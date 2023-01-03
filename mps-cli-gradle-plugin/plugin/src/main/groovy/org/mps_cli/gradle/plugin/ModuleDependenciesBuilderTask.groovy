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

class ModuleDependenciesBuilderTask extends DefaultTask {

    @Input
    List<String> sourcesDir;

    @Internal
    Map<SSolution, Set<SSolution>> solution2AllUpstreamDependencies = [:];

    @Internal
    Map<SSolution, Set<SSolution>> solution2AllDownstreamDependencies = [:];

    ModuleDependenciesBuilderTask() {
        group("MPS-CLI")
        description("build the upstream/downstream dependencies for all solutions based on MPS files from 'sourceDir'")
    }

    @TaskAction
    def buildModuleDependencies() {
        def builder = new SSolutionsRepositoryBuilder(buildingStrategy: BuildingDepthEnum.MODULE_DEPENDENCIES_ONLY)
        SLanguageBuilder.clear()
        sourcesDir.each {
            def dir = new File(it).getAbsoluteFile().canonicalPath
            println("loading models from directory: " + dir)
            builder.build(dir)
        }

        for (SSolution sol : builder.repo.solutions) {
            Set<SSolution> dependencies = [].toSet()
            collectUpstreamDependencies(builder.repo, sol, dependencies)
            solution2AllUpstreamDependencies[sol] = dependencies
        }

        for (SSolution currentSol : solution2AllUpstreamDependencies.keySet()) {
            Set<SSolution> downstreamDeps = [].toSet()
            for (SSolution sol : solution2AllUpstreamDependencies.keySet()) {
                if (solution2AllUpstreamDependencies[sol].contains(currentSol)) {
                    downstreamDeps.add(sol)
                }
            }
            solution2AllDownstreamDependencies[currentSol] = downstreamDeps
        }
    }

    def collectUpstreamDependencies(SRepository repo, SSolution sol, Set<SSolution> dependencies) {
        sol.dependencies.each {
            def dependency = it.resolve(repo)
            if (dependency != null && !dependencies.contains(dependency)) {
                dependencies.add(dependency)
                collectUpstreamDependencies(repo, dependency, dependencies)
            }
        }
    }

}