package org.mps_cli.model.builder.file_per_root_persistency

import groovy.xml.XmlParser
import org.mps_cli.model.SModel
import org.mps_cli.model.builder.AbstractRootNodeBuilder

class RootNodeFromMpsrBuilder extends AbstractRootNodeBuilder {


    def build(File mpsrFile, SModel sModel) {
        def model = new XmlParser().parse(mpsrFile)
        collectRegistryInfo(model)
        Node xmlNode = model.node.get(0)
        def res = collectNodes(xmlNode, null, sModel)
        res
    }

}
