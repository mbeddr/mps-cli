package org.mps_cli.model

class SModelRef {

    String referencedModelId

    SModel resolve(SRepository repo) {
        repo.id2models()[referencedModelId]
    }
}
