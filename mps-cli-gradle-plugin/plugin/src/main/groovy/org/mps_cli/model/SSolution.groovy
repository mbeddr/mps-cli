package org.mps_cli.model

class SSolution {
    String name
    String solutionId
    List<SModel> models = []
    List<SModuleRef> dependencies = []
}
