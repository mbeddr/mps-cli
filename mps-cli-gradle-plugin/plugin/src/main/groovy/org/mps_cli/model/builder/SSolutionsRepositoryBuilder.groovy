package org.mps_cli.model.builder

import groovy.time.TimeCategory
import groovy.time.TimeDuration
import org.mps_cli.model.SRepository

import static groovy.io.FileType.FILES

class SSolutionsRepositoryBuilder {

    def build(String path) {
        Date start = new Date()

        def filePath = new File(path)
        def filterSolutionDefinitions = ~/.*\.msd$/
        def solutionsDirectories = []
        filePath.traverse type : FILES, nameFilter : filterSolutionDefinitions, {
            solutionsDirectories.add(it.parentFile)
        }

        def repo = new SRepository()
        repo.name = path

        solutionsDirectories.each {
            def solutionBuilder = new SSolutionBuilder()
            def solution = solutionBuilder.build(it.absolutePath)
            repo.solutions.add(solution)
        }

        repo.languages.addAll(SLanguageBuilder.allLanguages())

        Date stop = new Date()
        TimeDuration td = TimeCategory.minus( stop, start )
        println "${td} for handling ${path}"

        repo
    }

}
