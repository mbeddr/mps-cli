package org.mps_cli.cone_of_influence

import groovy.transform.Immutable
import org.mps_cli.model.SModel
import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SRepository

import javax.annotation.Nullable

class ConeOfInfluenceComputer {

    SRepository repository

    @Immutable
    class Result {
        @Nullable List<SModel> affectedModels
        List<SModuleBase> affectedModules
        List<SModuleBase> affectedModulesAndUpstreamDependencies

        List getAt(int idx) {
            switch (idx) {
                case 0: return affectedModels
                case 1: return affectedModules
                case 2: return affectedModulesAndUpstreamDependencies
                default: throw new RuntimeException("Result has 3 fields")
            }
        }
    }

    Result computeConeOfInfluence(
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
            def modulesUniverse = module2AllUpstreamDependencies.keySet().toList()

            new Result(affectedModules: modulesUniverse, affectedModulesAndUpstreamDependencies: modulesUniverse)
        } else if (modifiedEntities.foundMissingModels) {
            println("Some models moved or deleted. Computing cone of influence based on modules.")
            def (modules, modulesAndUpstreamDependencies) = (
                    computeGeneric(modifiedEntities.modules, module2AllUpstreamDependencies, module2AllDownstreamDependencies))

            new Result(affectedModules: modules, affectedModulesAndUpstreamDependencies: modulesAndUpstreamDependencies)
        } else {
            println("Computing cone of influence based on models.")
            def (models2AllUpstreamDependencies, models2AllDownstreamDependencies) = EntityDependenciesBuilder.buildModelDependencies(repository)

            def (models, modelsAndUpstreamDependencies) = (
                    computeGeneric(modifiedEntities.models, models2AllUpstreamDependencies, models2AllDownstreamDependencies))

            new Result(
                    affectedModels: models,
                    affectedModules: models.myModule.unique(),
                    affectedModulesAndUpstreamDependencies: modelsAndUpstreamDependencies.myModule.unique())
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

        [allAffectedEntities.toList(), allAffectedEntitiesAndUpstreamDependencies.toList()]
    }
}
