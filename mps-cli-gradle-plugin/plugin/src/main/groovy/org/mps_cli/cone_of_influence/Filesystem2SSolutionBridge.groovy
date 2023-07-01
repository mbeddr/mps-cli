package org.mps_cli.cone_of_influence

import static groovy.io.FileType.FILES

class Filesystem2SSolutionBridge {

    /** Returns a list of .msd Files representing the modified modules. **/
    static List<File> computeModulesWhichAreModifiedInCurrentBranch(String gitRepoRootLocation, String branchName) {
        def gitRepoLocation = new File(gitRepoRootLocation).canonicalPath
        def differentFiles = GitFacade.computeFilesWhichAreModifiedInCurrentBranch(gitRepoLocation, branchName)

        List<File> affectedModulesFiles = []
        def allAffectedFilesAreInsideSolutions = true
        differentFiles.each {
            if (it.endsWith('.msd'))
                affectedModulesFiles.add(new File(gitRepoLocation + File.separator + it))
            else {
                def filterSolutionFiles = ~/.*\.msd$/
                def myFile = new File(gitRepoLocation + File.separator + it).parentFile
                def affectedModuleFound = false
                while (myFile != null) {
                    if (myFile.exists()) {
                        myFile.traverse(type: FILES, maxDepth: 0, nameFilter: filterSolutionFiles) {
                            affectedModuleFound = true; affectedModulesFiles.add(it) }
                    }
                    if (affectedModuleFound) break
                    myFile = myFile.parentFile
                }
                if (!affectedModuleFound) allAffectedFilesAreInsideSolutions = false
            }
        }

        affectedModulesFiles
    }
}
