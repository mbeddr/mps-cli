package org.mps_cli.model

class SModuleRef {
    String referencedModuleId

    SSolution resolve(SRepository repo) {
        repo.id2solutions()[referencedModuleId]
    }
}
