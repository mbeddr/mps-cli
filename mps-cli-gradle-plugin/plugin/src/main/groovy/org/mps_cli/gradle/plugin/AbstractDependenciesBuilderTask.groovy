package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.Internal
import org.mps_cli.model.SRepository
import org.mps_cli.model.builder.SModulesRepositoryBuilder

abstract class AbstractDependenciesBuilderTask extends DefaultTask {

    protected SModulesRepositoryBuilder builder;

    @Input
    List<String> sourcesDir;

    @Internal
    SRepository repository;

    abstract List<Object> allEntities();
    abstract List<Object> directDependencies(Object entity);

    def buildEntityDependencies(Map<?, Set<?>> entity2AllUpstreamDependencies,
                                Map<?, Set<?>> entity2AllDownstreamDependencies) {
        repository = builder.buildAll(sourcesDir)

        for (Object entity : allEntities()) {
            Set<Object> dependencies = [].toSet()
            collectUpstreamDependencies(repository, entity, dependencies)
            entity2AllUpstreamDependencies[entity] = dependencies
        }

        for (Object currentEntity : entity2AllUpstreamDependencies.keySet()) {
            Set<Object> downstreamDeps = [].toSet()
            for (Object entity : entity2AllUpstreamDependencies.keySet()) {
                if (entity2AllUpstreamDependencies[entity].contains(currentEntity)) {
                    downstreamDeps.add(entity)
                }
            }
            entity2AllDownstreamDependencies[currentEntity] = downstreamDeps
        }
    }

    def collectUpstreamDependencies(SRepository repo, Object entity, Set<Object> dependencies) {
        directDependencies(entity).each {
            def dependency = it.resolve(repo)
            if (dependency != null && !dependencies.contains(dependency)) {
                dependencies.add(dependency)
                collectUpstreamDependencies(repo, dependency, dependencies)
            }
        }
    }

}