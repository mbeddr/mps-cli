package org.mps_cli.model.builder.default_persistency

import groovy.time.TimeCategory
import groovy.time.TimeDuration
import groovy.xml.XmlParser
import org.mps_cli.model.SModel
import org.mps_cli.model.builder.AbstractModelBuilder
import org.mps_cli.model.builder.BuildingDepthEnum
import org.mps_cli.model.builder.file_per_root_persistency.RootNodeFromMpsrBuilder

import static groovy.io.FileType.FILES

class SModelBuilderForDefaultPersistency extends AbstractModelBuilder {

    def build(String pathToMsdFile) {
        Date start = new Date()

        def modelXML = new XmlParser().parse(pathToMsdFile)
        def sModel = buildModelFromXML(modelXML)

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
