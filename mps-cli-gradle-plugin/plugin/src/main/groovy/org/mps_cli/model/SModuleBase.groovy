package org.mps_cli.model

abstract class SModuleBase {
    String moduleId
    String pathToModuleFile
    List<SModel> models = []
    List<SModuleRef> dependencies = []

    def abstract String name();
}
