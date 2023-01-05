package org.mps_cli.gradle.plugin

import org.gradle.api.Project
import org.gradle.api.Plugin

/**
 * A plugin for handling MPS models from command-line.
 */
class MpsCliGradlePluginPlugin implements Plugin<Project> {
    void apply(Project project) {
        project.tasks.register('buildModel', ModelBuilderTask);
        project.tasks.register('printLanguageInfo', PrintLanguageInfoTask);
        project.tasks.register('buildModuleDependencies', ModuleDependenciesBuilderTask);
        project.tasks.register('buildModelDependencies', ModelDependenciesBuilderTask);
        project.tasks.register('computeConeOfInfluence', ConeOfInfluenceComputerTask);
    }
}
