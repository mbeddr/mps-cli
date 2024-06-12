/*
 * This Groovy source file was generated by the Gradle 'init' task.
 */
package org.mps_cli.gradle.plugin

class ConeOfInfluenceComputerTest extends TestBase {

    def buildFileText(String coneOfInfluenceSpec) {
        """
            plugins {
                id('com.mbeddr.mps_cli')
            }
            
            computeConeOfInfluence {
               $coneOfInfluenceSpec 
               gitRepoRootLocation = '../../../../../../../../../'
               sourcesDir = ['../../../../../../../../../mps_test_projects/mps_cli_lanuse_file_per_root'] 
            }
            
            task printConeOfInfluence {
                dependsOn computeConeOfInfluence
                doLast {
                    def affectedSolutions = computeConeOfInfluence.affectedSolutions
                    println "all affected solutions: \${affectedSolutions.collect { it.name }.sort()}"
                    def affectedModels = computeConeOfInfluence.affectedModels
                    println "all affected models: \${affectedModels.collect { it.name }.sort()}"
                }
            }
        """
    }

    def twoExpectedSolutions() {
        "all affected solutions: [mps.cli.lanuse.library_second, mps.cli.lanuse.library_top]"
    }

    def "from git diff"() {
        given:
        settingsFile << ""
        buildFile << buildFileText(
                "referenceBranchName = 'origin/testing/do_not_delete/cone_of_influence_test_01'")

        when:
        runTask("printConeOfInfluence")

        then:
        result.output.contains twoExpectedSolutions()
        result.output.contains "all affected models: []"
    }

    def "based on a modified root node in a model imported from other"() {
        given:
        settingsFile << ""
        buildFile << buildFileText(
                "modifiedFiles = ['mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.authors_top/_010_classical_authors.mpsr']")

        when:
        runTask("printConeOfInfluence")

        then:
        result.output.contains "Computing cone of influence based on models."
        result.output.contains twoExpectedSolutions()
        result.output.contains "all affected models: [mps.cli.lanuse.library_second.library_top, mps.cli.lanuse.library_top.authors_top, mps.cli.lanuse.library_top.library_top]"
    }

    def "based on a modified root node in a model not imported from other"() {
        given:
        settingsFile << ""
        buildFile << buildFileText(
                "modifiedFiles = ['mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.library_top/munich_library.mpsr']")

        when:
        runTask("printConeOfInfluence")

        then:
        result.output.contains "Computing cone of influence based on models."
        result.output.contains "all affected solutions: [mps.cli.lanuse.library_top]"
        result.output.contains "all affected models: [mps.cli.lanuse.library_top.library_top]"
    }

    def "based on a deleted model file"() {
        given:
        settingsFile << ""
        buildFile << buildFileText(
                "modifiedFiles = ['mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.deleted_model/.model']")

        when:
        runTask("printConeOfInfluence")

        then:
        result.output.contains "Some models moved or deleted. Computing cone of influence based on modules."
        result.output.contains twoExpectedSolutions()
        result.output.contains "all affected models: []"
    }

    def "based on a modified solution file"() {
        given:
        settingsFile << ""
        buildFile << buildFileText(
                "modifiedFiles = ['mps_test_projects/mps_cli_lanuse_file_per_root/solutions/mps.cli.lanuse.library_third/mps.cli.lanuse.library_third.msd']")

        when:
        runTask("printConeOfInfluence")

        then:
        result.output.contains "Some solutions moved or deleted. Skipping cone of influence."
        result.output.contains twoExpectedSolutions()
        result.output.contains "all affected models: []"
    }
}
