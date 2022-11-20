package org.mps_cli.model

class SModel {
    def String name
    def String modelId
    def List<SNode> rootNodes = []

    // caching
    def List<SNode> allNodes = new ArrayList<>(1024)
}
