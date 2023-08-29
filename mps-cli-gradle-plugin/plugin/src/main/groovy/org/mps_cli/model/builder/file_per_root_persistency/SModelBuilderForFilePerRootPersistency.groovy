package org.mps_cli.model.builder.file_per_root_persistency

import groovy.time.TimeCategory
import groovy.time.TimeDuration
import org.mps_cli.PathUtils
import org.mps_cli.model.builder.AbstractModelBuilder
import org.mps_cli.model.builder.BuildingDepthEnum
import org.slf4j.LoggerFactory

import java.nio.file.Files
import java.nio.file.Path

import static groovy.io.FileType.FILES

class SModelBuilderForFilePerRootPersistency extends AbstractModelBuilder {

    private def timingLogger = LoggerFactory.getLogger('repository-builder-timing')

    def build(Path path) {
        Date start = new Date()

        def pathToModelFile = path.resolve(".model")
        if (Files.notExists(pathToModelFile))
            return null;
        def modelXML = PathUtils.parseXml(pathToModelFile)
        def sModel = buildModelFromXML(modelXML)
        sModel.isFilePerRootPersistency = true
        sModel.pathToModelFile = PathUtils.pathToString(pathToModelFile)

        if (buildingStrategy != BuildingDepthEnum.MODEL_DEPENDENCIES_ONLY) {
            def filterFilePerRoot = ~/.*\.mpsr$/
            path.traverse type: FILES, nameFilter: filterFilePerRoot, {
                def builder = new RootNodeFromMpsrBuilder()
                def root = builder.build(it, sModel)
                sModel.rootNodes.add(root)
            }
        }

        Date stop = new Date()
        TimeDuration td = TimeCategory.minus( stop, start )
        timingLogger.info "{} for handling {}", td, path

        sModel
    }
}
