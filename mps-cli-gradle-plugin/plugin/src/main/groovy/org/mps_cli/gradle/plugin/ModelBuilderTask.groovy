package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.TaskAction
import org.mps_cli.model.SRepository
import org.mps_cli.model.builder.SSolutionsRepositoryBuilder

class ModelBuilderTask extends DefaultTask {

    @Input
    String sourcesDir;

    @TaskAction
    def buildModel() {
        def dir = new File(sourcesDir).getAbsoluteFile().canonicalPath
        println("loading models from directory: " + dir)

        def builder = new SSolutionsRepositoryBuilder()
        SRepository repository = builder.build(dir)

        project.ext.repository = repository
        println("number of solutions: " + repository.solutions.size)
    }

}
