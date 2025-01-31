package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.Internal
import org.gradle.api.tasks.TaskAction
import org.mps_cli.model.SRepository
import org.mps_cli.model.builder.SModulesRepositoryBuilder

class ModelBuilderTask extends DefaultTask {

    @Input
    List<String> sourcesDir;

    @Internal
    SRepository repository;

    ModelBuilderTask() {
        group = "MPS-CLI"
        description = "build the object model based on MPS files from 'sourceDir'"
    }

    @TaskAction
    def buildModel() {
        def builder = new SModulesRepositoryBuilder()

        repository = builder.buildAll(sourcesDir)
        println("number of solutions: " + repository.modules.size())
    }

}
