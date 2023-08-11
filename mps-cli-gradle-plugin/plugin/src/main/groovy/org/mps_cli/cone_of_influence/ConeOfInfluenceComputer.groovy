package org.mps_cli.cone_of_influence

import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SSolutionModule
import org.mps_cli.model.builder.SSolutionModuleBuilder

import java.nio.file.Files
import java.nio.file.Path

class ConeOfInfluenceComputer {

    Tuple2<List<SModuleBase>, List<SModuleBase>> computeConeOfInfluence(String gitRepoLocation, List<String> allModifiedFiles,
                                                                                Map<SModuleBase, Set<SModuleBase>> module2AllUpstreamDependencies,
                                                                                Map<SModuleBase, Set<SModuleBase>> module2AllDownstreamDependencies) {

        def modulesUniverse = module2AllUpstreamDependencies.keySet()

        List<Path> differentModulesFiles = Filesystem2SSolutionBridge.computeModulesWhichAreModifiedInCurrentBranch(gitRepoLocation, allModifiedFiles)

        println(">>>>>>>>>>>> All different modules files:")
        differentModulesFiles.each { println it }
        println("<<<<<<<<<<<<")

        // if any module is deleted (.msd file not available) then COI is the entire universe
        def notExistingSolutions = differentModulesFiles.findAll { Files.notExists(it) }
        if (notExistingSolutions) {
            println("Solutions ${notExistingSolutions.fileName} do not exist on current branch. The cone of influence is the entire set of solutions.")
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

        def allAffectedModules = (differentModulesFromBranch + downstreamDependenciesOfDirectlyAffectedModules).unique().toList()
        // compute upstream dependencies
        def upstreamAffectedModules = allAffectedModules.collectMany { module2AllUpstreamDependencies[it] }

        def allAffectedModulesAndUpstreamDependencies = (allAffectedModules + upstreamAffectedModules).unique().toList()

        new Tuple2(allAffectedModules, allAffectedModulesAndUpstreamDependencies)
    }
}
