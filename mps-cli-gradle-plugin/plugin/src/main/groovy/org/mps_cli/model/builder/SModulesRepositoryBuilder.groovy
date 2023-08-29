package org.mps_cli.model.builder

import groovy.time.TimeCategory
import groovy.time.TimeDuration
import org.mps_cli.model.SLanguage
import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SRepository

import java.nio.file.FileSystems
import java.nio.file.Path
import java.nio.file.Paths

import static groovy.io.FileType.FILES

class SModulesRepositoryBuilder {

    BuildingDepthEnum buildingStrategy = BuildingDepthEnum.COMPLETE_MODEL

    SRepository repo;

    private List<SLanguage> languages = [];
    private List<SModuleBase> modules = [];

    def build(String pathString) {
        Date start = new Date()

        Path path = Paths.get(pathString)
        collectModulesFromSources(path)
        collectModulesFromJars(path)

        languages.addAll(SLanguageBuilder.allLanguages())

        Date stop = new Date()
        TimeDuration td = TimeCategory.minus(stop, start)
        println "${td} for handling ${path}"

        repo = new SRepository(modules, languages)
    }

    private void collectModulesFromSources(Path path) {
        def filterLanguageDefinitions = ~/.*\.mpl$/
        List<Path> languagesDirectories = []
        path.traverse type: FILES, nameFilter: filterLanguageDefinitions, {
            languagesDirectories.add(it.parent)
        }

        languagesDirectories.each {
            def languageModuleBuilder = new SLanguageModuleBuilder(buildingStrategy : buildingStrategy)
            def language = languageModuleBuilder.build(it.toAbsolutePath())
            modules.add(language)
        }

        def filterSolutionDefinitions = ~/.*\.msd$/
        List<Path> solutionsDirectories = []
        path.traverse type: FILES, nameFilter: filterSolutionDefinitions, {
            solutionsDirectories.add(it.parent)
        }

        solutionsDirectories.each {
            def solutionModuleBuilder = new SSolutionModuleBuilder(buildingStrategy : buildingStrategy)
            def solution = solutionModuleBuilder.build(it.toAbsolutePath())
            modules.add(solution)
        }
    }

    private void collectModulesFromJars(Path path) {
        def filterJars = ~/.*\.jar$/
        List<Path> jarFiles = []
        path.traverse type: FILES, nameFilter: filterJars, {
            jarFiles.add(it)
        }

        jarFiles.each {
            FileSystems.newFileSystem(it, (ClassLoader) null).withCloseable {
                collectModulesFromSources(it.getPath("/"))
            }
        }
    }
}