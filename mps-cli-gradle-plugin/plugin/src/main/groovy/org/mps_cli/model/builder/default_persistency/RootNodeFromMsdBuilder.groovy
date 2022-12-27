package org.mps_cli.model.builder.default_persistency

import org.mps_cli.model.SModel
import org.mps_cli.model.builder.AbstractRootNodeBuilder

class RootNodeFromMsdBuilder extends AbstractRootNodeBuilder {

    def build(Node model, SModel sModel) {
        collectRegistryInfo(model)
        def res = []
        for (Node xmlNode : model.node)
            res.add(collectNodes(xmlNode, null, sModel))
        res
    }
}
