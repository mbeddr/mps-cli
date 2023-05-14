package org.mps_cli.gradle.plugin

class SolutionsModelBuildingTest extends TestBase {

    def "model extraction test"() {
        given:
        projectName = proj
        settingsFile << ""
        buildFile << "${buildPreamble()}" + '''

task printSolutionsInfo {
    dependsOn buildModel
    doLast {
        def repo = buildModel.repository
        
        def library_second = repo.modules.find { it.name.equals("mps.cli.lanuse.library_second") ||
                                                it.name.equals("mps.cli.lanuse.library_second.default_persistency") }
        def normalizedSolutionPath = library_second.pathToModuleFile.replace("/", "\\\\")
        println "solution $library_second.name is saved in directory $normalizedSolutionPath"
        
        def modules = repo.modules
        println "all modules: ${modules.collect { it.name }}"
        def solutionWithDependencies = modules.find { it.name.equals("mps.cli.lanuse.library_second") || 
                                                        it.name.equals("mps.cli.lanuse.library_second.default_persistency") }
        println "all modules on which 'mps.cli.lanuse.library_second' is dependent on: ${solutionWithDependencies.dependencies.collect { it.resolve(repo).name }}"
        
        def models = repo.allModels()
        println "all models: ${models.collect { it.name }}"
        
        def modelWithImports = models.find { it.name.equals("mps.cli.lanuse.library_second.library_top") ||
                                             it.name.equals("mps.cli.lanuse.library_second.default_persistency.library_top") }
        def normalizedModelPath = modelWithImports.pathToModelFile.replace("/", "\\\\")
        println "path to model $modelWithImports.name is $normalizedModelPath"
        println "all models imported by 'mps.cli.lanuse.library_second.library_top': ${modelWithImports.imports.collect { it.resolve(repo).name }}"
        
        def allNodes = repo.allNodes()
        println "concepts: ${allNodes.collect { it.concept.name }}"
        
        def authors = repo.nodesOfConcept("mps.cli.landefs.people.structure.Person")
        println "persons definitions: ${authors.collect { it.name }.sort()}"
        
        def books = repo.nodesOfConcept("mps.cli.landefs.library.structure.Book")
        println "books definitions: ${books.collect { it.name }.sort()}"
        
        def theMysteriousIsland = books.find { it.name.equals("The Mysterious Island") }
        println "'Mysterious Island' authors: ${theMysteriousIsland.authors.collect {it.person.resolve(repo).name }}"
        println "'Mysterious Island' publication date: ${theMysteriousIsland.publicationDate}"
        println "'Mysterious Island' available: ${theMysteriousIsland.available}"
        println "the solution containing the 'Mysterious Island' is: ${theMysteriousIsland.myModel.mySolution.name}"
        
        
        def magazines = repo.nodesOfConcept("mps.cli.landefs.library.structure.Magazine")
        println "magazines definitions: ${magazines.collect { it.name }}"
        
        def derSpiegel = magazines.find { it.name.equals("Der Spiegel") }
        println "'Der Spiegel' periodicity: ${derSpiegel.periodicity}"
    }
}

'''

        when:
        runTask("printSolutionsInfo")

        then:
        // check paths of solutions
        result.output.split("\n").any { it.contains("solution mps.cli.lanuse.library_second is saved in directory") &&
                it.contains("solutions\\mps.cli.lanuse.library_second\\mps.cli.lanuse.library_second.msd") ||
                it.contains("solution mps.cli.lanuse.library_second.default_persistency is saved in directory") &&
                it.contains("solutions\\mps.cli.lanuse.library_second.default_persistency\\mps.cli.lanuse.library_second.default_persistency.msd") ||
                it.contains("solution mps.cli.lanuse.library_second is saved in directory") &&
                it.contains("mps_cli_lanuse_binary\\mps_cli_lanuse_file_per_root.jar_tmp\\mps.cli.lanuse.library_second\\mps.cli.lanuse.library_second.msd")
        }

        // check dependencies between solutions
        result.output.contains("all modules on which 'mps.cli.lanuse.library_second' is dependent on: [mps.cli.lanuse.library_top]") ||
            result.output.contains("all modules on which 'mps.cli.lanuse.library_second' is dependent on: [mps.cli.lanuse.library_top.default_persistency]")

        // check that we have models
        result.output.contains library_top_dot_library_top
        result.output.contains library_top_dot_authors_top
        result.output.contains library_second_dot_library_top

        // check paths of models
        result.output.split("\n").any { it.contains("path to model mps.cli.lanuse.library_second.library_top is") &&
                                            it.contains("solutions\\mps.cli.lanuse.library_second\\models\\mps.cli.lanuse.library_second.library_top\\.model") ||
                                            it.contains("path to model mps.cli.lanuse.library_second.default_persistency.library_top is") &&
                                            it.contains("solutions\\mps.cli.lanuse.library_second.default_persistency\\models\\mps.cli.lanuse.library_second.default_persistency.library_top.mps") ||
                                            it.contains("path to model mps.cli.lanuse.library_second.library_top is") &&
                                            it.contains("mps_cli_lanuse_binary\\mps_cli_lanuse_file_per_root.jar_tmp\\mps.cli.lanuse.library_second\\models\\mps.cli.lanuse.library_second.library_top\\.model") }

        // check dependencies between models
        result.output.contains("all models imported by 'mps.cli.lanuse.library_second.library_top': [mps.cli.lanuse.library_top.authors_top]") ||
            result.output.contains("all models imported by 'mps.cli.lanuse.library_second.library_top': [mps.cli.lanuse.library_top.default_persistency.authors_top]")

        // check nodes by name
        // persons
        result.output.contains "persons definitions: [Jules Verne, Mark Twain]"

        // book
        result.output.contains "books definitions: [Five Weeks in Baloon, The Mysterious Island, Tom Sawyer, Tom Sawyer]"
        result.output.contains "'Mysterious Island' authors: [Jules Verne]"
        result.output.contains "'Mysterious Island' publication date: 1875"
        result.output.contains "'Mysterious Island' available: true"
        result.output.split("\n").any { it.startsWith("the solution containing the 'Mysterious Island' is: mps.cli.lanuse.library_top.default_persistency") ||
                it.startsWith("the solution containing the 'Mysterious Island' is: mps.cli.lanuse.library_top") }

        // magazine
        result.output.contains "magazines definitions: [Der Spiegel]"
        result.output.contains "'Der Spiegel' periodicity: 4Yb5JA31wzt/WEEKLY"

        where:
        proj                                 | library_top_dot_library_top                                  | library_top_dot_authors_top                                  | library_second_dot_library_top
        "mps_cli_lanuse_file_per_root"       | "mps.cli.lanuse.library_top.library_top"                     | "mps.cli.lanuse.library_top.authors_top"                     | "mps.cli.lanuse.library_second.library_top"
        "mps_cli_lanuse_default_persistency" | "mps.cli.lanuse.library_top.default_persistency.library_top" | "mps.cli.lanuse.library_top.default_persistency.authors_top" | "mps.cli.lanuse.library_second.default_persistency.library_top"
        "mps_cli_lanuse_binary"              | "mps.cli.lanuse.library_top.library_top"                     | "mps.cli.lanuse.library_top.authors_top"                     | "mps.cli.lanuse.library_second.library_top"
    }
}
