package org.mps_cli.cone_of_influence

import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths

import static groovy.io.FileType.FILES

class Filesystem2SSolutionBridge {

    static List<Path> computeModulesWhichAreModifiedInCurrentBranch(String gitRepoRootLocation, List<String> allModifiedFiles) {
        def gitRepoLocation = Paths.get(gitRepoRootLocation).toAbsolutePath().normalize()

        List<Path> affectedModulesFiles = []
        allModifiedFiles.each {
            if (it.endsWith('.msd'))
                affectedModulesFiles.add(gitRepoLocation.resolve(it))
            else {
                def filterSolutionFiles = ~/.*\.msd$/
                def myFile = gitRepoLocation.resolve(it).parent
                def affectedModuleFound = false
                while (myFile != null) {
                    if (Files.exists(myFile)) {
                        myFile.traverse(type: FILES, maxDepth: 0, nameFilter: filterSolutionFiles) {
                            affectedModuleFound = true; affectedModulesFiles.add(it) }
                    }
                    if (affectedModuleFound) break
                    myFile = myFile.parent
                }
            }
        }

        affectedModulesFiles
    }
}
