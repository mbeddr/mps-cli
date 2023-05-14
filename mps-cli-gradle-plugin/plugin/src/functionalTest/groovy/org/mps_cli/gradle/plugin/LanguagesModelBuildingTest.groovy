package org.mps_cli.gradle.plugin

class LanguagesModelBuildingTest extends TestBase {

    def "model extraction test"() {
        given:
        projectName = "landefs"
        settingsFile << ""
        buildFile << """ 
plugins {
    id('com.mbeddr.mps_cli')
}

buildModel {
   sourcesDir = ['../../../../../../../../../mps_test_projects/mps_cli_landefs']   
}""" + '''

task printSolutionsInfo {
    dependsOn buildModel
    doLast {
        def repo = buildModel.repository
        
        def library_lan = repo.modules.find { it.namespace.equals("mps.cli.landefs.library") }
        def normalizedModulePath = library_lan.pathToModuleFile.replace("/", "\\\\")
        println "library language $library_lan.namespace is saved in directory $normalizedModulePath"
        
        def modules = repo.modules
        println "all modules: ${modules.collect { it.name() }}"

    }
}

'''

        when:
        runTask("printSolutionsInfo")

        then:
        // check paths of languages
        result.output.split("\n").any { it.contains("library language mps.cli.landefs.library is saved in directory") &&
                it.contains("languages\\mps.cli.landefs.library\\mps.cli.landefs.library.mpl") }

        // check modules
        result.output.contains("all modules: [mps.cli.landefs.library, mps.cli.landefs.people, mps.cli.landefs.library.sandbox]")
    }
}
