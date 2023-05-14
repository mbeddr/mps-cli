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

    def projectName;

    def buildPreamble()
    {
        """ 
plugins {
    id('com.mbeddr.mps_cli')
}

buildModel {
   sourcesDir = ['../../../../../../../../../mps_test_projects/$projectName']   
}"""
    }

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
