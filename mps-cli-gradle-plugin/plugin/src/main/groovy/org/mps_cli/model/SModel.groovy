package org.mps_cli.model

class SModel {
    String name
    String modelId
    String pathToModelFile
    boolean isFilePerRootPersistency
    List<SNode> rootNodes = []
    List<SModelRef> imports = []

    // caching
    List<SNode> allNodes = new ArrayList<>(1024)

    Map<String, SNode> nodeId2Node() {
        allNodes.collectEntries {[it.id, it] }
    }
}
