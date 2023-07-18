package org.mps_cli.model.builder.file_per_root_persistency

import org.mps_cli.PathUtils
import org.mps_cli.model.SModel
import org.mps_cli.model.builder.AbstractRootNodeBuilder

import java.nio.file.Path

class RootNodeFromMpsrBuilder extends AbstractRootNodeBuilder {

    def build(Path mpsrFile, SModel sModel) {
        def model = PathUtils.parseXml(mpsrFile)
        collectRegistryInfo(model)
        Node xmlNode = model.node.get(0)
        def res = collectNodes(xmlNode, null, sModel)
        res
    }

}
