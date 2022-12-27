package org.mps_cli.model.builder

import org.mps_cli.model.SModel

class AbstractModelBuilder {

    SModel buildModelFromXML(Node modelXMLNode) {
        def sModel = new SModel()
        def ref = modelXMLNode.'@ref'
        sModel.modelId = ref.substring(0, ref.indexOf('('))
        sModel.name = ref.substring(ref.indexOf('(') + 1, ref.indexOf(')'))
        sModel
    }
}
