/*
 * This Groovy source file was generated by the Gradle 'init' task.
 */
package org.mps_cli.gradle.plugin

class PluginSmokeTest extends TestBase {

    def "'buildModel' task starts"() {
        given:
        projectName = proj
        settingsFile << ""
        buildFile << "${buildPreamble()}"

        when:
        runTask("buildModel")

        then:
        result.output.contains("mps_test_projects" + File.separator + proj)
        result.output.contains("number of solutions: 2")

        where:
        proj                                 | _
        "mps_cli_lanuse_file_per_root"       | _
        "mps_cli_lanuse_default_persistency" | _
    }
}
