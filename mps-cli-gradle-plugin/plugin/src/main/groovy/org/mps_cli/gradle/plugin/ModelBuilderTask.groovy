package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.Internal
import org.gradle.api.tasks.TaskAction
import org.gradle.plugins.ide.eclipse.model.Output
import org.mps_cli.model.SRepository
import org.mps_cli.model.builder.SLanguageBuilder
import org.mps_cli.model.builder.SSolutionsRepositoryBuilder

class ModelBuilderTask extends DefaultTask {

    @Input
    List<String> sourcesDir;

    @Internal
    SRepository repository;

    ModelBuilderTask() {
        group("MPS-CLI")
        description("build the object model based on MPS files from 'sourceDir'")
    }

    @TaskAction
    def buildModel() {
        def builder = new SSolutionsRepositoryBuilder()
        SLanguageBuilder.clear()
        sourcesDir.each {
            def dir = new File(it).getAbsoluteFile().canonicalPath
            println("loading models from directory: " + dir)
            builder.build(dir)
        }
        //setProperty("repository", repository)
        repository = builder.repo

        println("number of solutions: " + repository.solutions.size)
    }

}
