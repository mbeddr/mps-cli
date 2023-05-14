package org.mps_cli.model

class SModuleRef {
    String referencedModuleId

    SSolutionModule resolve(SRepository repo) {
        repo.id2modules()[referencedModuleId]
    }
}
