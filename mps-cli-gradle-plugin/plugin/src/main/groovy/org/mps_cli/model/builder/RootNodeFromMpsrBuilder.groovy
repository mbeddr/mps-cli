package org.mps_cli.model.builder

import groovy.xml.XmlParser
import org.mps_cli.model.SConcept
import org.mps_cli.model.SLanguage
import org.mps_cli.model.SModel
import org.mps_cli.model.SNode
import org.mps_cli.model.SNodeRef

class RootNodeFromMpsrBuilder {

    Map<String, SConcept> conceptsIds2SConcept = [:]
    Map<String, SConcept> membersIds2SConcept = [:]
    Map<String, String> childrenIds2Names = [:]
    Map<String, String> referenceIds2Names = [:]
    Map<String, String> propertyIds2Names = [:]
    Map<String, String> importsIndex2ImportedModelIds = [:]

    def build(File mpsrFile, SModel sModel) {
        def model = new XmlParser().parse(mpsrFile)
        collectRegistryInfo(model)
        Node xmlNode = model.node.get(0)
        def res = collectNodes(xmlNode, null, sModel)
        res
    }

    def collectNodes(Node xmlNode, SNode parent, SModel sModel) {
        SNode sNode = new SNode(parent, childrenIds2Names[xmlNode.'@role'], sModel)
        sModel.allNodes.add(sNode)
        SConcept concept = conceptsIds2SConcept[xmlNode.'@concept']
        sNode.concept = concept
        sNode.id = xmlNode.'@id'

        def conceptOwnerOfChildRole = membersIds2SConcept[xmlNode.'@role']
        if (conceptOwnerOfChildRole != concept) concept.superConcepts.add(conceptOwnerOfChildRole)

        xmlNode.property.each {
            def propertyName = propertyIds2Names[it.'@role']
            sNode.properties[propertyName] = it.'@value'

            def conceptOwnerOfProperty = membersIds2SConcept[it.'@role']
            if (conceptOwnerOfProperty != concept) concept.superConcepts.add(conceptOwnerOfProperty)
        }
        xmlNode.node.each {
            def childNode = collectNodes(it, sNode, sModel)
            sNode.children.add(childNode)
        }
        xmlNode.ref.each {
            if (it.'@to' != null) {
                String[] parts = it.'@to'.split(":")
                def targetModelId = importsIndex2ImportedModelIds[parts[0]]
                def targetNodeId = parts[1]
                def referenceName = referenceIds2Names[it.'@role']
                sNode.refs[referenceName] = new SNodeRef(referencedModelId : targetModelId, referencedNodeId : targetNodeId)

                def conceptOwnerOfReference = membersIds2SConcept[it.'@role']
                if (conceptOwnerOfReference != concept) concept.superConcepts.add(conceptOwnerOfReference)
            }
        }

        sNode
    }

    def collectRegistryInfo(Node model) {
        model.registry.language.each { language ->
            SLanguage sLanguage = SLanguageBuilder.getLanguage(language.'@name')
            language.concept.each { concept ->
                SConcept sConcept = SLanguageBuilder.getConcept(sLanguage, concept.'@name')
                conceptsIds2SConcept[concept.'@index'] = sConcept
                concept.child.each { child ->
                    def childRoleName = child.'@name'
                    childrenIds2Names[child.'@index'] = childRoleName
                    membersIds2SConcept[child.'@index'] = sConcept
                    sConcept.children.add(childRoleName)
                }
                concept.reference.each { reference ->
                    def referenceRoleName = reference.'@name'
                    referenceIds2Names[reference.'@index'] = referenceRoleName
                    membersIds2SConcept[reference.'@index'] = sConcept
                    sConcept.references.add(referenceRoleName)
                }
                concept.property.each { property ->
                    def propertyName = property.'@name'
                    propertyIds2Names[property.'@index'] = propertyName
                    membersIds2SConcept[property.'@index'] = sConcept
                    sConcept.properties.add(propertyName)
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
