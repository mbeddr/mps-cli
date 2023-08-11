package org.mps_cli.model.builder

import groovy.time.TimeCategory
import groovy.time.TimeDuration
import org.mps_cli.PathUtils
import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SModuleRef
import org.mps_cli.model.builder.default_persistency.SModelBuilderForDefaultPersistency
import org.mps_cli.model.builder.file_per_root_persistency.SModelBuilderForFilePerRootPersistency

import java.nio.file.Files
import java.nio.file.Path

import static java.util.stream.Collectors.toList

abstract class AbstractSModuleBuilder {

    BuildingDepthEnum buildingStrategy = BuildingDepthEnum.COMPLETE_MODEL;

    protected Node moduleXML;

    abstract Path moduleFile(Path pathToModuleDirectory);

    def build(Path pathToModuleDirectory) {
        Date start = new Date()

        def solutionFile = moduleFile(pathToModuleDirectory)
        SModuleBase sModuleBase = extractModuleCoreInfo(solutionFile)
        sModuleBase.pathToModuleFile = PathUtils.pathToString(solutionFile)

        for (Node dep : moduleXML.dependencies.dependency) {
            def moduleRefString = dep.text()
            def moduleIdRefString = moduleRefString.substring(0, moduleRefString.indexOf('('))
            sModuleBase.dependencies.add(new SModuleRef(referencedModuleId: moduleIdRefString))
        }

        if (buildingStrategy != BuildingDepthEnum.MODULE_DEPENDENCIES_ONLY) {
            def modelsDir = pathToModuleDirectory.resolve("models")
            def modelFiles = Files.exists(modelsDir) ? Files.list(modelsDir).collect(toList()) : []
            modelFiles.findAll(Files.&isDirectory).each {
                def modelBuilder = new SModelBuilderForFilePerRootPersistency(buildingStrategy: buildingStrategy)
                def model = modelBuilder.build(it.toAbsolutePath())
                if (model != null) {
                    model.myModule = sModuleBase
                    sModuleBase.models.add(model)
                }
            }
            modelFiles.findAll { it.fileName.toString().endsWith(".mps") }.each {
                def modelBuilder = new SModelBuilderForDefaultPersistency(buildingStrategy: buildingStrategy)
                def model = modelBuilder.build(it.toAbsolutePath())
                sModuleBase.models.add(model)
                model.myModule = sModuleBase
            }
        }

        Date stop = new Date()
        TimeDuration td = TimeCategory.minus(stop, start)
        println "${td} for handling ${pathToModuleDirectory}"

        sModuleBase
    }

    abstract SModuleBase extractModuleCoreInfo(Path solutionFile);
}
