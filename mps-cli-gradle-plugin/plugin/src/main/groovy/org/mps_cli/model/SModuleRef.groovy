package org.mps_cli.model

class SModuleRef {
    String referencedModuleId

    SModuleBase resolve(SRepository repo) {
        repo.id2modules()[referencedModuleId]
    }
}
