package org.mps_cli.model

class SSolution {
    String name
    String solutionId
    String pathToSolutionFile
    List<SModel> models = []
    List<SModuleRef> dependencies = []
}
