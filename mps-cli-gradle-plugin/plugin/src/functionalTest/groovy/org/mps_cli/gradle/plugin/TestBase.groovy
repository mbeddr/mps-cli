package org.mps_cli.gradle.plugin

import org.gradle.testkit.runner.GradleRunner
import spock.lang.Specification
import spock.lang.TempDir

class TestBase extends Specification {

    @TempDir
    protected File projectDir

    protected getBuildFile() {
        new File(projectDir, "build.gradle")
    }

    protected getSettingsFile() {
        new File(projectDir, "settings.gradle")
    }

    def buildPreamble = """ 
plugins {
    id('org.mps_cli.gradle.plugin')
}

buildModel {
   sourcesDir = '../../../../../../../../../mps_test_projects/mps_cli_lanuse'   
}"""

    def result

    protected void runTask(String taskName) {
        def runner = GradleRunner.create()
        runner.forwardOutput()
        runner.withPluginClasspath()
        runner.withArguments([taskName])
        runner.withProjectDir(projectDir)
        result = runner.build()
    }
}
