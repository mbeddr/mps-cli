/*
 * This Groovy source file was generated by the Gradle 'init' task.
 */
package org.mps_cli.gradle.plugin

class ConeOfInfluenceComputerTest_02 extends TestBase {

    def "cone of influence computer test"() {
        given:
        settingsFile << ""
        buildFile << '''

plugins {
    id('com.mbeddr.mps_cli')
}

buildModuleDependencies {
   sourcesDir = ['../../../../../../../../../mps_test_projects/mps_cli_lanuse_file_per_root']      
}

computeConeOfInfluence {
   referenceBranchName = "origin/testing/do_not_delete/cone_of_influence_test_02" 
   gitRepoRootLocation = '../../../../../../../../../'
}

task printConeOfInfluence {
    dependsOn computeConeOfInfluence
    doLast {
        def affectedSolutions = computeConeOfInfluence.affectedSolutions
        println "all affected solutions: ${affectedSolutions.collect { it.name }.sort()}"
    }
}
'''

        when:
        runTask("printConeOfInfluence")

        then:
        result.output.contains "Solution mps.cli.lanuse.library_top2.msd does not exist on current branch. COI cannot be computed and is the entire universe of solutions."
        result.output.contains "all affected solutions: [mps.cli.lanuse.library_second, mps.cli.lanuse.library_top]"
    }
}
