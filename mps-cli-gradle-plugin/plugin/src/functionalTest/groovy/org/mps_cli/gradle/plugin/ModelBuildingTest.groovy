package org.mps_cli.gradle.plugin

class ModelBuildingTest extends TestBase {

    def "model attributes test"() {
        given:
        projectName = "mps_cli_lanuse_model_attributes"
        settingsFile << ""
        buildFile << """ 
plugins {
    id('com.mbeddr.mps_cli')
}

buildModel {
   sourcesDir = ['../../../../../../../../../mps_test_projects/mps_cli_lanuse_model_attributes']   
}""" + '''

task printModelsInfo {
    dependsOn buildModel
    doLast {
        def repo = buildModel.repository
        
        def models = repo.allModels()
        println "all the models: ${models.collect { it.name }}"
        
        def generatedModels = models.findAll { it.isDoNotGenerate == false }
        println "all models enabled for generation: ${generatedModels.collect { it.name }}}"
        
        def notGeneratedModels = models.find { it.isDoNotGenerate == true }
        println "all models disabled for generation: ${notGeneratedModels.collect { it.name }}}"
    }
}

'''

        when:
        runTask("printModelsInfo")

        then:
        // check the models
        result.output.contains "mps_cli_lanuse_model_attributes.default_generation"
        result.output.contains "mps_cli_lanuse_model_attributes.enable_generation"
        result.output.contains "mps_cli_lanuse_model_attributes.disable_generation"

        // check models that are generated
        result.output.contains "all models enabled for generation: [mps_cli_lanuse_model_attributes.default_generation, mps_cli_lanuse_model_attributes.enable_generation]"

        // check models that are NOT generated
        result.output.contains "all models disabled for generation: [mps_cli_lanuse_model_attributes.disable_generation]"
    }
}
