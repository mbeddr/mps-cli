package org.mps_cli.cone_of_influence

import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SSolutionModule
import org.mps_cli.model.builder.SSolutionModuleBuilder

class ConeOfInfluenceComputer {

    Tuple2<List<SModuleBase>, List<SModuleBase>> computeConeOfInfluence(String gitRepoLocation, String branchName,
                                                                                Map<SModuleBase, Set<SModuleBase>> module2AllUpstreamDependencies,
                                                                                Map<SModuleBase, Set<SModuleBase>> module2AllDownstreamDependencies) {

        def modulesUniverse = module2AllUpstreamDependencies.keySet()

        List<File> differentModulesFiles = Filesystem2SSolutionBridge.computeModulesWhichAreModifiedInCurrentBranch(gitRepoLocation, branchName)
        println("all different modules files: " + differentModulesFiles)

        // if any module is deleted (.msd file not available) then COI is the entire universe
        if (differentModulesFiles.any {!it.exists() }) {
            File notExistingSolution = differentModulesFiles.find {!it.exists() }
            print("Solution ${notExistingSolution.name} does not exist on current branch. COI cannot be computed and is the entire universe of solutions.")
            return new Tuple2(modulesUniverse.toList(), modulesUniverse.toList())
        }

        List<String> differentModulesIds = differentModulesFiles.collect {
            SSolutionModuleBuilder builder = new SSolutionModuleBuilder()
            SSolutionModule sol = builder.extractModuleCoreInfo(it)
            sol.moduleId
        }

        // directly affected modules
        def differentModulesFromBranch = modulesUniverse.findAll {differentModulesIds.contains(it.moduleId) }
        // indirectly potentially affected modules
        def downstreamDependenciesOfDirectlyAffectedModules = differentModulesFromBranch.collectMany {module2AllDownstreamDependencies[it] }

        def allAffectedModuless = (differentModulesFromBranch + downstreamDependenciesOfDirectlyAffectedModules).unique().toList()
        // compute upstream dependencies
        def upstreamAffectedModules = allAffectedModuless.collectMany { module2AllUpstreamDependencies[it] }

        def allAffectedModulesAndUpstreamDependencies = (allAffectedModuless + upstreamAffectedModules).unique().toList()

        new Tuple2(allAffectedModuless, allAffectedModulesAndUpstreamDependencies)
    }
}
