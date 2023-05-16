package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.Internal
import org.gradle.api.tasks.TaskAction
import org.mps_cli.cone_of_influence.ConeOfInfluenceComputer

class ConeOfInfluenceComputerTask extends DefaultTask{

    @Input
    String gitRepoRootLocation

    @Input
    String referenceBranchName

    @Internal
    List<String> affectedSolutions;

    @Internal
    List<String> affectedSolutionsAndUpstreamDependencies;

    ConeOfInfluenceComputerTask() {
        group "MPS-CLI"
        description "computes the solutions potentially affected (and their dependencies) of the changes from current branch compared to 'referenceBranchName' from the 'gitRootRepoLocation'"
        dependsOn "buildModuleDependencies"
    }

    @TaskAction
    def computeConeOfInfluence() {
        def solution2AllUpstreamDependencies = project.buildModuleDependencies.module2AllUpstreamDependencies
        def solution2AllDownstreamDependencies = project.buildModuleDependencies.module2AllDownstreamDependencies

        ConeOfInfluenceComputer coiComputer = new ConeOfInfluenceComputer()
        def res = coiComputer.computeConeOfInfluence(gitRepoRootLocation, referenceBranchName,
                                    solution2AllUpstreamDependencies,
                                    solution2AllDownstreamDependencies)
        affectedSolutions = res.v1
        affectedSolutionsAndUpstreamDependencies = res.v2
    }
}
