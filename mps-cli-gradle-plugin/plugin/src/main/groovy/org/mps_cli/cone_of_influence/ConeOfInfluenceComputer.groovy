package org.mps_cli.cone_of_influence

import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SRepository

class ConeOfInfluenceComputer {

    SRepository repository

    Tuple2<List<SModuleBase>, List<SModuleBase>> computeConeOfInfluence(
            String rootLocation,
            List<String> allModifiedFiles
    ) {
        def bridge = new Filesystem2SSolutionBridge(repository: repository)
        def modifiedEntities = bridge.computeModifiedEntities(rootLocation, allModifiedFiles)

        println(">>>>>>>>>>>> Modified modules:")
        modifiedEntities.modules.each { println it.pathToModuleFile }
        println(">>>>>>>>>>>> Modified models:")
        modifiedEntities.models.each { println it.pathToModelFile }
        println("<<<<<<<<<<<<")

        def (module2AllUpstreamDependencies, module2AllDownstreamDependencies) = EntityDependenciesBuilder.buildModuleDependencies(repository)

        if (modifiedEntities.foundMissingModules) {
            println("Some solutions moved or deleted. Skipping cone of influence.")
            def modulesUniverse = module2AllUpstreamDependencies.keySet()
            new Tuple2(modulesUniverse.toList(), modulesUniverse.toList())
        } else if (modifiedEntities.foundMissingModels) {
            println("Some models moved or deleted. Computing cone of influence based on modules.")
            computeGeneric(modifiedEntities.modules, module2AllUpstreamDependencies, module2AllDownstreamDependencies)
        } else {
            println("Computing cone of influence based on models.")
            def (models2AllUpstreamDependencies, models2AllDownstreamDependencies) = EntityDependenciesBuilder.buildModelDependencies(repository)

            def (models, modelsAndUpstreamDependencies) =
                computeGeneric(modifiedEntities.models, models2AllUpstreamDependencies, models2AllDownstreamDependencies)

            [models.myModule.unique(), modelsAndUpstreamDependencies.myModule.unique()]
        }
    }

    private static <Entity> Tuple2<List<Entity>, List<Entity>> computeGeneric(
            Set<Entity> modifiedEntities,
            Map<Entity, Set<Entity>> upstreamDependencies,
            Map<Entity, Set<Entity>> downstreamDependencies
    ) {
        def transitivelyAffectedEntities = modifiedEntities.collectMany { downstreamDependencies[it] ?: [] }
        def allAffectedEntities = modifiedEntities + transitivelyAffectedEntities

        def upstreamAffectedEntities = allAffectedEntities.collectMany { upstreamDependencies[it] ?: [] }
        def allAffectedEntitiesAndUpstreamDependencies = allAffectedEntities + upstreamAffectedEntities

        new Tuple2(allAffectedEntities.toList(), allAffectedEntitiesAndUpstreamDependencies.toList())
    }
}
