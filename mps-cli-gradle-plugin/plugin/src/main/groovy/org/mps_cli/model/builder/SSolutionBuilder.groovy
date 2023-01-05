package org.mps_cli.model.builder

import groovy.time.TimeCategory
import groovy.time.TimeDuration
import groovy.xml.XmlParser
import org.mps_cli.model.SModelRef
import org.mps_cli.model.SModuleRef
import org.mps_cli.model.SSolution
import org.mps_cli.model.builder.default_persistency.SModelBuilderForDefaultPersistency
import org.mps_cli.model.builder.file_per_root_persistency.SModelBuilderForFilePerRootPersistency

class SSolutionBuilder {

    BuildingDepthEnum buildingStrategy = BuildingDepthEnum.COMPLETE_MODEL;

    private Node solutionXML;

    def build(String path) {
        Date start = new Date()

        def filePath = new File(path)
        def solutionFile = filePath.listFiles().find {it.name.endsWith(".msd")}
        SSolution sSolution = extractSolutionCoreInfo(solutionFile)

        for(Node dep : solutionXML.dependencies.dependency) {
            def moduleRefString = dep.text()
            def moduleIdRefString = moduleRefString.substring(0, moduleRefString.indexOf('('))
            sSolution.dependencies.add(new SModuleRef(referencedModuleId : moduleIdRefString))
        }

        if (buildingStrategy != BuildingDepthEnum.MODULE_DEPENDENCIES_ONLY) {
            def modelFiles = new File(filePath, "models").listFiles()
            modelFiles.findAll {it.isDirectory() }.each {
                def modelBuilder = new SModelBuilderForFilePerRootPersistency(buildingStrategy: buildingStrategy)
                def model = modelBuilder.build(it.absolutePath)
                if (model != null)
                    sSolution.models.add(model)
            }
            modelFiles.findAll {it.name.endsWith(".mps") }.each {
                def modelBuilder = new SModelBuilderForDefaultPersistency(buildingStrategy: buildingStrategy)
                def model = modelBuilder.build(it.absolutePath)
                sSolution.models.add(model)
            }
        }

        Date stop = new Date()
        TimeDuration td = TimeCategory.minus( stop, start )
        println "${td} for handling ${path}"

        sSolution
    }

    public SSolution extractSolutionCoreInfo(File solutionFile) {
        solutionXML = new XmlParser().parse(solutionFile)
        def sSolution = new SSolution()
        sSolution.name = solutionXML.'@name'
        sSolution.solutionId = solutionXML.'@uuid'
        sSolution
    }
}
