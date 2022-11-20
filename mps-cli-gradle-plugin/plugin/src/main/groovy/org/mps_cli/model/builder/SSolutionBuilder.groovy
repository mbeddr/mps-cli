package org.mps_cli.model.builder

import groovy.time.TimeCategory
import groovy.time.TimeDuration
import groovy.xml.XmlParser
import org.mps_cli.model.SSolution

class SSolutionBuilder {

    def build(path) {
        Date start = new Date()

        def filePath = new File(path)
        def solutionFile = filePath.listFiles().find {it.name.endsWith(".msd")}
        def solutionXML = new XmlParser().parse(solutionFile)
        def sSolution = new SSolution()
        sSolution.name = solutionXML.'@name'
        sSolution.solutionId = solutionXML.'@uuid'

        def modelFiles = new File(filePath, "models").listFiles()
        modelFiles.findAll {it.isDirectory() }.each {
            def modelBuilder = new SModelBuilder()
            def model = modelBuilder.build(it.absolutePath)
            sSolution.models.add(model)
        }

        Date stop = new Date()
        TimeDuration td = TimeCategory.minus( stop, start )
        println "${td} for handling ${path}"

        sSolution
    }
}
