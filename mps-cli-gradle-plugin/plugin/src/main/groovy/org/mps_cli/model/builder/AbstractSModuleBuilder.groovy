package org.mps_cli.model.builder

import groovy.time.TimeCategory
import groovy.time.TimeDuration
import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SModuleRef
import org.mps_cli.model.builder.default_persistency.SModelBuilderForDefaultPersistency
import org.mps_cli.model.builder.file_per_root_persistency.SModelBuilderForFilePerRootPersistency

abstract class AbstractSModuleBuilder {

    BuildingDepthEnum buildingStrategy = BuildingDepthEnum.COMPLETE_MODEL;

    protected Node moduleXML;

    def abstract File moduleFile(File pathToModuleDirectory);

    def build(String path) {
        Date start = new Date()

        def pathToModuleDirectory = new File(path)
        def solutionFile = moduleFile(pathToModuleDirectory)
        SModuleBase sModuleBase = extractModuleCoreInfo(solutionFile)
        sModuleBase.pathToModuleFile = solutionFile.absolutePath

        for(Node dep : moduleXML.dependencies.dependency) {
            def moduleRefString = dep.text()
            def moduleIdRefString = moduleRefString.substring(0, moduleRefString.indexOf('('))
            sModuleBase.dependencies.add(new SModuleRef(referencedModuleId : moduleIdRefString))
        }

        if (buildingStrategy != BuildingDepthEnum.MODULE_DEPENDENCIES_ONLY) {
            def modelFiles = new File(pathToModuleDirectory, "models").listFiles()
            modelFiles.findAll {it.isDirectory() }.each {
                def modelBuilder = new SModelBuilderForFilePerRootPersistency(buildingStrategy: buildingStrategy)
                def model = modelBuilder.build(it.absolutePath)
                if (model != null) {
                    model.myModule = sModuleBase
                    sModuleBase.models.add(model)
                }
            }
            modelFiles.findAll {it.name.endsWith(".mps") }.each {
                def modelBuilder = new SModelBuilderForDefaultPersistency(buildingStrategy: buildingStrategy)
                def model = modelBuilder.build(it.absolutePath)
                sModuleBase.models.add(model)
                model.myModule = sModuleBase
            }
        }

        Date stop = new Date()
        TimeDuration td = TimeCategory.minus( stop, start )
        println "${td} for handling ${path}"

        sModuleBase
    }

    def abstract SModuleBase extractModuleCoreInfo(File solutionFile);
}
