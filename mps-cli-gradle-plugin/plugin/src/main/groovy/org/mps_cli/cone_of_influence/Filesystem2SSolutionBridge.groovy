package org.mps_cli.cone_of_influence

import static groovy.io.FileType.FILES

class Filesystem2SSolutionBridge {

    static List<File> computeModulesWhichAreDifferentFromBranch(String gitRepoRootLocation, String branchName) {
        def differentFiles = GitFacade.computeFilesWhichAreDifferentFromBranch(gitRepoRootLocation, branchName)

        List<File> affectedModulesFiles = []
        def allAffectedFilesAreInsideSolutions = true
        differentFiles.each {
            if (it.endsWith('.msd'))
                affectedModulesFiles.add(new File(gitRepoRootLocation + File.separator + it))
            else {
                def filterSolutionFiles = ~/.*\.msd$/
                def myFile = new File(gitRepoRootLocation + File.separator + it).parentFile
                def affectedModuleFound = false
                while (myFile != null) {
                    myFile.traverse(type: FILES, maxDepth: 0, nameFilter: filterSolutionFiles) {
                        affectedModuleFound = true; affectedModulesFiles.add(it) }
                    if (affectedModuleFound) break
                    myFile = myFile.parentFile
                }
                if (!affectedModuleFound) allAffectedFilesAreInsideSolutions = false
            }
        }

        affectedModulesFiles
    }
}
