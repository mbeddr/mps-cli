package org.mps_cli.model.builder

import groovy.xml.XmlParser
import org.mps_cli.model.SLanguageModule
import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SSolutionModule

class SLanguageModuleBuilder extends AbstractSModuleBuilder {

    @Override
    File moduleFile(File pathToModuleDirectory) {
        pathToModuleDirectory.listFiles().find {it.name.endsWith(".mpl")}
    }

    @Override
    SModuleBase extractModuleCoreInfo(File solutionFile) {
        moduleXML = new XmlParser().parse(solutionFile)
        def sLanguageModule = new SLanguageModule()
        sLanguageModule.namespace = moduleXML.'@namespace'
        sLanguageModule.moduleId = moduleXML.'@uuid'
        sLanguageModule
    }
}
