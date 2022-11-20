package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.TaskAction
import org.mps_cli.model.SSolutionsUniverse
import org.mps_cli.model.builder.SSolutionsUniverseBuilder

class PrintLanguageLanguageDefinitionTask extends DefaultTask {

    @Input
    String sourcesDir;

    @TaskAction
    def printLanguageDefinition() {
        println("loading models from directory: " + sourcesDir)

        def builder = new SSolutionsUniverseBuilder()
        SSolutionsUniverse universe = builder.build(sourcesDir)

        println("number of solutions: " + universe.solutions.size)
    }
}
