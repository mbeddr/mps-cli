package org.mps_cli.cone_of_influence

import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SSolutionModule
import org.mps_cli.model.builder.SSolutionModuleBuilder

import java.nio.file.Path

class ConeOfInfluenceComputer {

    Tuple2<List<SModuleBase>, List<SModuleBase>> computeConeOfInfluence(String gitRepoLocation, List<String> allModifiedFiles,
                                                                                Map<SModuleBase, Set<SModuleBase>> module2AllUpstreamDependencies,
                                                                                Map<SModuleBase, Set<SModuleBase>> module2AllDownstreamDependencies) {

        List<Path> differentModulesFiles = Filesystem2SSolutionBridge.computeModulesWhichAreModifiedInCurrentBranch(gitRepoLocation, allModifiedFiles)

        List<String> differentModulesIds = differentModulesFiles.collect {
            SSolutionModuleBuilder builder = new SSolutionModuleBuilder()
            SSolutionModule sol = builder.extractModuleCoreInfo(it)
            sol.moduleId
        }

        // directly affected modules
        def differentModulesFromBranch = module2AllUpstreamDependencies.keySet().findAll {differentModulesIds.contains(it.moduleId) }
        // indirectly potentially affected modules
        def downstreamDependenciesOfDirectlyAffectedModules = differentModulesFromBranch.collectMany {module2AllDownstreamDependencies[it] }

        def allAffectedModules = (differentModulesFromBranch + downstreamDependenciesOfDirectlyAffectedModules).unique().toList()
        // compute upstream dependencies
        def upstreamAffectedModules = allAffectedModules.collectMany { module2AllUpstreamDependencies[it] }

        def allAffectedModulesAndUpstreamDependencies = (allAffectedModules + upstreamAffectedModules).unique().toList()

        new Tuple2(allAffectedModules, allAffectedModulesAndUpstreamDependencies)
    }
}
