package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.Internal
import org.gradle.api.tasks.Optional
import org.gradle.api.tasks.TaskAction
import org.mps_cli.cone_of_influence.ConeOfInfluenceComputer
import org.mps_cli.cone_of_influence.GitFacade
import org.mps_cli.model.SModuleBase

class ConeOfInfluenceComputerTask extends DefaultTask {

    @Input
    String gitRepoRootLocation

    @Optional
    @Input
    String referenceBranchName

    @Optional
    @Input
    List<String> modifiedFiles

    @Internal
    List<SModuleBase> affectedSolutions

    @Internal
    List<SModuleBase> affectedSolutionsAndUpstreamDependencies

    ConeOfInfluenceComputerTask() {
        group "MPS-CLI"
        description "computes the solutions potentially affected (and their dependencies) of the changes from current branch compared to 'referenceBranchName' from the 'gitRootRepoLocation'"
        dependsOn "buildModuleDependencies"
    }

    @TaskAction
    def computeConeOfInfluence() {
        if (modifiedFiles == null && referenceBranchName == null ||
                modifiedFiles != null && referenceBranchName != null) {
            throw new RuntimeException("You must specify either 'modifiedFiles' or 'referenceBranchName' input parameter")
        }

        def solution2AllUpstreamDependencies = project.buildModuleDependencies.module2AllUpstreamDependencies
        def solution2AllDownstreamDependencies = project.buildModuleDependencies.module2AllDownstreamDependencies

        def allModifiedFiles = modifiedFiles != null ? modifiedFiles :
                GitFacade.computeFilesWhichAreModifiedInCurrentBranch(gitRepoRootLocation, referenceBranchName)

        ConeOfInfluenceComputer coiComputer = new ConeOfInfluenceComputer()
        (affectedSolutions, affectedSolutionsAndUpstreamDependencies) = coiComputer.computeConeOfInfluence(
                gitRepoRootLocation,
                allModifiedFiles,
                solution2AllUpstreamDependencies,
                solution2AllDownstreamDependencies)
    }
}
