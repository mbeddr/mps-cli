package org.mps_cli.cone_of_influence

import org.mps_cli.model.SSolution
import org.mps_cli.model.builder.SSolutionBuilder

class ConeOfInfluenceComputer {

    Tuple2<List<SSolution>, List<SSolution>> computeConeOfInfluence(String gitRepoLocation, String branchName,
                                            Map<SSolution, Set<SSolution>> solution2AllUpstreamDependencies,
                                            Map<SSolution, Set<SSolution>> solution2AllDownstreamDependencies) {

        List<File> differentModulesFiles = Filesystem2SSolutionBridge.computeModulesWhichAreDifferentFromBranch(gitRepoLocation, branchName)

        List<String> differentSolutionsIds = differentModulesFiles.collect {
            SSolutionBuilder builder = new SSolutionBuilder()
            SSolution sol = builder.extractSolutionCoreInfo(it)
            sol.solutionId
        }

        // directly affected solutions
        def differentSolutionsFromBranch = solution2AllUpstreamDependencies.keySet().findAll {differentSolutionsIds.contains(it.solutionId) }
        // indirectly potentially affected solutions
        def downstreamDependenciesOfDirectlyAffectedSolutions = differentSolutionsFromBranch.collectMany {solution2AllDownstreamDependencies[it] }

        def allAffectedSolutions = (differentSolutionsFromBranch + downstreamDependenciesOfDirectlyAffectedSolutions).unique().toList()
        // compute upstream dependencies
        def upstreamAffectedSolutions = allAffectedSolutions.collectMany { solution2AllUpstreamDependencies[it] }

        def allAffectedSolutionsAndUpstreamDependencies = (allAffectedSolutions + upstreamAffectedSolutions).unique().toList()

        new Tuple2(allAffectedSolutions, allAffectedSolutionsAndUpstreamDependencies)
    }
}
