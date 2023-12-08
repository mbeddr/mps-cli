package org.mps_cli

import org.mps_cli.model.SSolutionModule;
import org.mps_cli.model.builder.BuildingDepthEnum
import org.mps_cli.model.builder.SModulesRepositoryBuilder

class MpsCliDemo {

    static void main(String[] args) {
        if (args.length != 1) {
            print("Usage: 'gradlew run --args PATH_TO_DIRECTORY_CONTAINING_MPS_SOLUTIONS")
            exit(1)
        }
        println("Loading models from '${args[0]}' ...")
        def builder = new SModulesRepositoryBuilder(buildingStrategy: BuildingDepthEnum.COMPLETE_MODEL)
        def repo = builder.build(args[0])

        println("Statistics:")
        println("\t number of modules: " + repo.modules.findAll {it instanceof SSolutionModule }.size())
        println("\t number of models: " + repo.allModels().size())
        println("\t number of nodes: " + repo.allNodes().size())
    }
}
