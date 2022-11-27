package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.Task
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.TaskAction
import org.mps_cli.model.SSolutionsUniverse
import org.mps_cli.model.builder.SSolutionsUniverseBuilder

class ModelBuilderTask extends DefaultTask {

    @Input
    String sourcesDir;

    @TaskAction
    def buildModel() {
        def dir = new File(sourcesDir).getAbsoluteFile().canonicalPath
        println("loading models from directory: " + dir)

        def builder = new SSolutionsUniverseBuilder()
        SSolutionsUniverse universe = builder.build(dir)

        project.ext.universe = universe
        println("number of solutions: " + universe.solutions.size)
    }

}
