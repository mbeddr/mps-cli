package org.mps_cli.cone_of_influence

import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SSolutionModule
import org.mps_cli.model.builder.SSolutionModuleBuilder

class ConeOfInfluenceComputer {

    Tuple2<List<SModuleBase>, List<SModuleBase>> computeConeOfInfluence(String gitRepoLocation, String branchName,
                                                                                Map<SModuleBase, Set<SModuleBase>> module2AllUpstreamDependencies,
                                                                                Map<SModuleBase, Set<SModuleBase>> module2AllDownstreamDependencies) {

        List<File> differentModulesFiles = Filesystem2SSolutionBridge.computeModulesWhichAreDifferentFromBranch(gitRepoLocation, branchName)

        List<String> differentModulesIds = differentModulesFiles.collect {
            SSolutionModuleBuilder builder = new SSolutionModuleBuilder()
            SSolutionModule sol = builder.extractModuleCoreInfo(it)
            sol.moduleId
        }

        // directly affected modules
        def differentModulesFromBranch = module2AllUpstreamDependencies.keySet().findAll {differentModulesIds.contains(it.moduleId) }
        // indirectly potentially affected modules
        def downstreamDependenciesOfDirectlyAffectedModules = differentModulesFromBranch.collectMany {module2AllDownstreamDependencies[it] }

        def allAffectedModuless = (differentModulesFromBranch + downstreamDependenciesOfDirectlyAffectedModules).unique().toList()
        // compute upstream dependencies
        def upstreamAffectedModules = allAffectedModuless.collectMany { module2AllUpstreamDependencies[it] }

        def allAffectedModulesAndUpstreamDependencies = (allAffectedModuless + upstreamAffectedModules).unique().toList()

        new Tuple2(allAffectedModuless, allAffectedModulesAndUpstreamDependencies)
    }
}
