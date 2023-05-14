package org.mps_cli.model.builder


import groovy.xml.XmlParser
import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SSolutionModule

class SSolutionModuleBuilder extends AbstractSModuleBuilder {

    @Override
    File moduleFile(File pathToModuleDirectory) {
        pathToModuleDirectory.listFiles().find {it.name.endsWith(".msd")}
    }

    @Override
    SModuleBase extractModuleCoreInfo(File solutionFile) {
        moduleXML = new XmlParser().parse(solutionFile)
        def sSolution = new SSolutionModule()
        sSolution.name = moduleXML.'@name'
        sSolution.moduleId = moduleXML.'@uuid'
        sSolution
    }
}
