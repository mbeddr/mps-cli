package org.mps_cli.model.builder

import groovy.time.TimeCategory
import groovy.time.TimeDuration
import org.mps_cli.model.SRepository

import java.nio.file.Files
import java.nio.file.Paths
import java.util.zip.ZipFile

import static groovy.io.FileType.FILES

class SSolutionsRepositoryBuilder {

    BuildingDepthEnum buildingStrategy = BuildingDepthEnum.COMPLETE_MODEL

    def repo = new SRepository()

    def build(String path) {
        Date start = new Date()

        collectSolutionsFromSources(path)
        collectSolutionsFromJars(path)

        repo.languages.addAll(SLanguageBuilder.allLanguages())

        Date stop = new Date()
        TimeDuration td = TimeCategory.minus(stop, start)
        println "${td} for handling ${path}"
        repo
    }

    private void collectSolutionsFromSources(String path) {
        def filePath = new File(path)
        def filterSolutionDefinitions = ~/.*\.msd$/
        def solutionsDirectories = []
        filePath.traverse type: FILES, nameFilter: filterSolutionDefinitions, {
            solutionsDirectories.add(it.parentFile)
        }

        solutionsDirectories.each {
            def solutionBuilder = new SSolutionBuilder(buildingStrategy : buildingStrategy)
            def solution = solutionBuilder.build(it.absolutePath)
            repo.solutions.add(solution)
        }
    }

    private void collectSolutionsFromJars(String path) {
        def filePath = new File(path)
        def filterJars = ~/.*\.jar$/
        List<File> jarFiles = []
        filePath.traverse type: FILES, nameFilter: filterJars, {
            jarFiles.add(it)
        }

        jarFiles.each {
            def destinationDirectoryToUnpackJar = new File(it.parent, it.name + "_tmp")
            Date start = new Date()
            unpackJar(it, destinationDirectoryToUnpackJar)
            Date stop = new Date()
            TimeDuration td = TimeCategory.minus(stop, start)
            println "${td} - extracting jar file ${it.name} to $destinationDirectoryToUnpackJar"
            collectSolutionsFromSources(destinationDirectoryToUnpackJar.absolutePath)
            destinationDirectoryToUnpackJar.deleteDir()
        }
    }

    def unpackJar(File jarFile, File destinationDirectory) {
        destinationDirectory.mkdirs()
        def zipFile = new ZipFile(jarFile)
        zipFile.entries().each { it ->
            def path = Paths.get(destinationDirectory.absolutePath + File.separator + it.name)
            if(it.directory){
                Files.createDirectories(path)
            }
            else {
                def parentDir = path.getParent()
                if (!Files.exists(parentDir)) {
                    Files.createDirectories(parentDir)
                }
                Files.copy(zipFile.getInputStream(it), path)
            }
        }
    }
}