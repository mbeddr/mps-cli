package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.Internal
import org.gradle.api.tasks.Optional
import org.gradle.api.tasks.TaskAction
import org.mps_cli.cone_of_influence.ConeOfInfluenceComputer
import org.mps_cli.cone_of_influence.GitFacade
import org.mps_cli.model.SModel
import org.mps_cli.model.SModuleBase
import org.mps_cli.model.builder.BuildingDepthEnum
import org.mps_cli.model.builder.SModulesRepositoryBuilder

class ConeOfInfluenceComputerTask extends DefaultTask {

    @Input
    String gitRepoRootLocation

    @Optional
    @Input
    List<String> sourcesDir;

    @Optional
    @Input
    String referenceBranchName

    @Optional
    @Input
    List<String> modifiedFiles

    @Internal
    List<SModel> affectedModels

    @Internal
    List<SModuleBase> affectedSolutions

    @Internal
    List<SModuleBase> affectedSolutionsAndUpstreamDependencies

    ConeOfInfluenceComputerTask() {
        group = "MPS-CLI"
        description = "computes the solutions potentially affected (and their dependencies) of the changes from current branch compared to 'referenceBranchName' from the 'gitRootRepoLocation'"
    }

    @TaskAction
    def computeConeOfInfluence() {
        if (modifiedFiles == null && referenceBranchName == null ||
                modifiedFiles != null && referenceBranchName != null) {
            throw new RuntimeException("You must specify either 'modifiedFiles' or 'referenceBranchName' input parameter")
        }
        sourcesDir ?= [gitRepoRootLocation]

        def allModifiedFiles = modifiedFiles != null ? modifiedFiles :
                GitFacade.computeFilesWhichAreModifiedInCurrentBranch(gitRepoRootLocation, referenceBranchName)

        def builder = new SModulesRepositoryBuilder(buildingStrategy: BuildingDepthEnum.MODEL_DEPENDENCIES_ONLY)
        def repository = builder.buildAll(sourcesDir)
        def coiComputer = new ConeOfInfluenceComputer(repository: repository)

        (affectedModels, affectedSolutions, affectedSolutionsAndUpstreamDependencies) =
                coiComputer.computeConeOfInfluence(gitRepoRootLocation, allModifiedFiles)
    }
}
