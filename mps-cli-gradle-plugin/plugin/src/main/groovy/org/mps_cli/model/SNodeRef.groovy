package org.mps_cli.model

class SNodeRef {
    String referencedModelId
    String referencedNodeId

    SNode resolve(SRepository repo) {
        SModel model = repo.id2models()[referencedModelId]
        model.nodeId2Node()[referencedNodeId]
    }
}
