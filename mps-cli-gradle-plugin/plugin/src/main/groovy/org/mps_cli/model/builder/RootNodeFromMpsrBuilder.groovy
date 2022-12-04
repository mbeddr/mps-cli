package org.mps_cli.model.builder


import groovy.xml.XmlParser
import org.mps_cli.model.SModel
import org.mps_cli.model.SNode
import org.mps_cli.model.SNodeRef

class RootNodeFromMpsrBuilder {

    def conceptsIds2Names = [:]
    def childrenIds2Names = [:]
    def referenceIds2Names = [:]
    def propertyIds2Names = [:]
    def importsIndex2ImportedModelIds = [:]

    def build(File mpsrFile, SModel sModel) {
        def model = new XmlParser().parse(mpsrFile)
        collectRegistryInfo(model)
        Node xmlNode = model.node.get(0)
        def res = collectNodes(xmlNode, null, sModel)
        res
    }

    def collectNodes(xmlNode, parent, sModel) {
        def sNode = new SNode(parent, childrenIds2Names[xmlNode.'@role'], sModel)
        sModel.allNodes.add(sNode)
        sNode.concept = conceptsIds2Names[xmlNode.'@concept']
        sNode.id = xmlNode.'@id'

        xmlNode.property.each { sNode.properties[propertyIds2Names[it.'@role']] = it.'@value' }
        xmlNode.node.each { sNode.children.add(collectNodes(it, sNode, sModel))  }
        xmlNode.ref.each {
            String[] parts = it.'@to'.split(":")
            def targetModelId = importsIndex2ImportedModelIds[parts[0]]
            def targetNodeId = parts[1]
            sNode.refs[referenceIds2Names[it.'@role']] = new SNodeRef(referencedModelId : targetModelId, referencedNodeId : targetNodeId)
        }

        sNode
    }

    def collectRegistryInfo(model) {
        model.registry.language.each { language ->
                language.concept.each { concept ->
                    conceptsIds2Names[concept.'@index'] = concept.'@name'
                    concept.child.each { child ->
                        childrenIds2Names[child.'@index'] = child.'@name'
                    }
                    concept.reference.each { reference ->
                        referenceIds2Names[reference.'@index'] = reference.'@name'
                    }
                    concept.property.each { property ->
                        propertyIds2Names[property.'@index'] = property.'@name'
                    }
                }
        }
        model.imports.import.each { _import ->
            // e.g. <import index="q0v6" ref="r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed(mps.cli.lanuse.library_top.authors_top)" implicit="true" />
            String importedModelIdAndName = _import.'@ref'
            importsIndex2ImportedModelIds[_import.'@index'] = importedModelIdAndName.substring(0, importedModelIdAndName.indexOf("("))
        }
    }
}
