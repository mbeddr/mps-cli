package org.mps_cli.model.builder


import groovy.xml.XmlParser
import org.mps_cli.model.SModel
import org.mps_cli.model.SNode

class RootNodeFromMpsrBuilder {

    def conceptsIds2Names = [:]
    def childrenIds2Names = [:]
    def referenceIds2Names = [:]
    def propertyIds2Names = [:]

    def build(File mpsrFile, SModel sModel) {
        def model = new XmlParser().parse(mpsrFile)
        collectRegistryInfo(model)
        def res = collectNodes(model.node, null, sModel)
        res
    }

    def collectNodes(xmlNode, parent, sModel) {
        def sNode = new SNode(parent, childrenIds2Names[xmlNode.'@role'])
        sModel.allNodes.add(sNode)
        sNode.concept = conceptsIds2Names[xmlNode.'@concept']
        sNode.id = xmlNode.'@id'

        xmlNode.node.each { sNode.children.add(collectNodes(it, sNode, sModel))  }
        xmlNode.property.each { sNode.properties[propertyIds2Names[it.'@role']] = it.'@value' }

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
    }
}
