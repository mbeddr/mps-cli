package org.mps_cli.model.builder

import org.mps_cli.PathUtils
import org.mps_cli.model.SLanguageModule
import org.mps_cli.model.SModuleBase

import java.nio.file.Files
import java.nio.file.Path

class SLanguageModuleBuilder extends AbstractSModuleBuilder {

    @Override
    Path moduleFile(Path pathToModuleDirectory) {
        (Path) Files.list(pathToModuleDirectory).find { it.fileName.toString().endsWith(".mpl") }
    }

    @Override
    SModuleBase extractModuleCoreInfo(Path solutionFile) {
        moduleXML = PathUtils.parseXml(solutionFile)
        def sLanguageModule = new SLanguageModule()
        sLanguageModule.namespace = moduleXML.'@namespace'
        sLanguageModule.moduleId = moduleXML.'@uuid'
        sLanguageModule
    }
}
