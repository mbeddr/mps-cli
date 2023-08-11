package org.mps_cli.model.builder

import org.mps_cli.PathUtils
import org.mps_cli.model.SSolutionModule

import java.nio.file.Files
import java.nio.file.Path

class SSolutionModuleBuilder extends AbstractSModuleBuilder {

    @Override
    Path moduleFile(Path pathToModuleDirectory) {
        (Path) Files.list(pathToModuleDirectory).find { it.fileName.toString().endsWith(".msd") }
    }

    @Override
    SSolutionModule extractModuleCoreInfo(Path solutionFile) {

        moduleXML = PathUtils.parseXml(solutionFile)
        def sSolution = new SSolutionModule()
        sSolution.name = moduleXML.'@name'
        sSolution.moduleId = moduleXML.'@uuid'
        sSolution
    }
}
