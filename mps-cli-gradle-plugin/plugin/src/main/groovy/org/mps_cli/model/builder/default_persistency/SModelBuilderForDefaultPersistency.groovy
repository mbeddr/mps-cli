package org.mps_cli.model.builder.default_persistency

import groovy.time.TimeCategory
import groovy.time.TimeDuration
import org.mps_cli.PathUtils
import org.mps_cli.model.builder.AbstractModelBuilder
import org.mps_cli.model.builder.BuildingDepthEnum

import java.nio.file.Path

class SModelBuilderForDefaultPersistency extends AbstractModelBuilder {

    def build(Path pathToMsdFile) {
        Date start = new Date()

        def modelXML = PathUtils.parseXml(pathToMsdFile)
        def sModel = buildModelFromXML(modelXML)
        sModel.isFilePerRootPersistency = false
        sModel.pathToModelFile = PathUtils.pathToString(pathToMsdFile)

        if (buildingStrategy != BuildingDepthEnum.MODEL_DEPENDENCIES_ONLY) {
            def builder = new RootNodeFromMsdBuilder()
            def roots = builder.build(modelXML, sModel)
            sModel.rootNodes.addAll(roots)
        }

        Date stop = new Date()
        TimeDuration td = TimeCategory.minus( stop, start )
        println "${td} for handling ${pathToMsdFile}"

        sModel
    }
}
