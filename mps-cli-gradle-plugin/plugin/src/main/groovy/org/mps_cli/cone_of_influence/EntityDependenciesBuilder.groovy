package org.mps_cli.cone_of_influence

import org.mps_cli.model.SRepository

class EntityDependenciesBuilder {

    static def buildModuleDependencies(SRepository repository) {
        buildEntityDependencies(repository, { it.modules }, { it.dependencies })
    }

    static def buildModelDependencies(SRepository repository) {
        buildEntityDependencies(repository, { it.allModels() }, { it.imports })
    }

    static <Entity> Tuple2 buildEntityDependencies(
            SRepository repository,
            Closure<List<Entity>> allEntities,
            Closure<List<Object>> directDependencyRefs
    ) {
        Map<Entity, Set<Entity>> entity2AllUpstreamDependencies = [:]
        Map<Entity, Set<Entity>> entity2AllDownstreamDependencies = [:]

        for (Entity entity : allEntities(repository)) {
            entity2AllUpstreamDependencies[entity] = collectUpstreamDependencies(entity, repository, directDependencyRefs)
        }

        for (Entity currentEntity : entity2AllUpstreamDependencies.keySet()) {
            entity2AllDownstreamDependencies[currentEntity] = entity2AllUpstreamDependencies.findResults {
                entity, dependencies -> dependencies.contains(currentEntity) ? entity : null
            }.toSet()
        }

        [entity2AllUpstreamDependencies, entity2AllDownstreamDependencies]
    }

    private static <Entity> Set<Entity> collectUpstreamDependencies(
            Entity entity,
            SRepository repository,
            Closure<List<Object>> directDependencyRefs
    ) {
        Set<Entity> result = []
        Queue<Entity> queue = new ArrayDeque<>([entity])

        while (!queue.isEmpty()) {
            Entity currentEntity = queue.poll()
            directDependencyRefs(currentEntity).each {
                Entity dependency = it.resolve(repository)
                if (dependency != null && !result.contains(dependency)) {
                    result.add(dependency)
                    queue.add(dependency)
                }
            }
        }

        result
    }
}
