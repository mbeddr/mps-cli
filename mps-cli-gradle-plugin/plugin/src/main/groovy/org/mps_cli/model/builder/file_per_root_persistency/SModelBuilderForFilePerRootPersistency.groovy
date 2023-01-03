package org.mps_cli.model.builder.file_per_root_persistency

import groovy.time.TimeCategory
import groovy.time.TimeDuration
import groovy.xml.XmlParser
import org.mps_cli.model.SModel
import org.mps_cli.model.builder.AbstractModelBuilder
import org.mps_cli.model.builder.BuildingDepthEnum

import static groovy.io.FileType.FILES

class SModelBuilderForFilePerRootPersistency extends AbstractModelBuilder {

    def build(String path) {
        Date start = new Date()

        def pathToModelFile = path + File.separator + ".model"
        if (!new File(pathToModelFile).exists())
            return null;
        def modelXML = new XmlParser().parse(pathToModelFile)
        def sModel = buildModelFromXML(modelXML)

        if (buildingStrategy != BuildingDepthEnum.MODEL_DEPENDENCIES_ONLY) {
            def filePath = new File(path)
            def filterFilePerRoot = ~/.*\.mpsr$/
            filePath.traverse type: FILES, nameFilter: filterFilePerRoot, {
                def builder = new RootNodeFromMpsrBuilder()
                def root = builder.build(it, sModel)
                sModel.rootNodes.add(root)
            }
        }

        Date stop = new Date()
        TimeDuration td = TimeCategory.minus( stop, start )
        println "${td} for handling ${path}"

        sModel
    }


}
