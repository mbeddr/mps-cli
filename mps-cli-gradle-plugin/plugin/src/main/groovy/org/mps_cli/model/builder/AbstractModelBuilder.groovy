package org.mps_cli.model.builder

import org.mps_cli.model.SModel
import org.mps_cli.model.SModelRef

class AbstractModelBuilder {

    SModel buildModelFromXML(Node modelXMLNode) {
        def sModel = new SModel()
        def ref = modelXMLNode.'@ref'
        sModel.modelId = ref.substring(0, ref.indexOf('('))
        sModel.name = ref.substring(ref.indexOf('(') + 1, ref.indexOf(')'))

        for (Node imp : modelXMLNode.imports.import) {
            def modelRefString = imp.'@ref'
            def modelIdRefString = modelRefString.substring(0, ref.indexOf('('))
            sModel.imports.add(new SModelRef(referencedModelId : modelIdRefString))
        }

        sModel
    }
}
