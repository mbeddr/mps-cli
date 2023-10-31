

import { SAbstractConceptLink, SConcept, SProperty } from '../sconcept';
import { SConceptRegistry, SLanguageRegistry, SLinkRegistry, SNode, SPropertyRegistry, SRootNode, SRootNodeRegistry } from '../snode';
import { SLanguageBuilder } from './slanguage_builder';
import { childrenByTagName } from './utils';

export function buildRootNode(doc : Document) : SRootNode {
    const modelNode : Element = doc.getElementsByTagName("model")[0];
    const registryElement = modelNode.getElementsByTagName("registry")[0];
    const registry = buildRootNodeRegistry(registryElement)

    const rootNodeElement = modelNode.getElementsByTagName("node")[0];
    const rootNodeConceptIndex = rootNodeElement.attributes.getNamedItem("concept")!.value
    const rootNodeId = rootNodeElement.attributes.getNamedItem("id")!.value
    const rootNodeConcept = registry.getConceptByIndex(rootNodeConceptIndex)
    const mySRootNode = new SRootNode(registry, rootNodeConcept, rootNodeId);

    populateNodePropertiesAndLinks(rootNodeElement, mySRootNode, registry)
    buildChildNodes(rootNodeElement, mySRootNode, registry)

    return mySRootNode;
}


function buildChildNodes(parentNodeElement : Element, parent : SNode, registry : SRootNodeRegistry) {
    for(var nodeElement of parentNodeElement.getElementsByTagName("node")) {
        const nodeConceptIndex = nodeElement.attributes.getNamedItem("concept")!.value
        const nodeId = nodeElement.attributes.getNamedItem("id")!.value
        const nodeConcept = registry.getConceptByIndex(nodeConceptIndex)
        const nodeRoleInParentString = nodeElement.attributes.getNamedItem("role")!.value
        const linkInParent = registry.getLinkByIndex(nodeRoleInParentString)
        const node = new SNode(nodeConcept, nodeId)
        parent.addLink(linkInParent, node)
        populateNodePropertiesAndLinks(nodeElement, node, registry)

        buildChildNodes(nodeElement, node, registry)
    }
}

function populateNodePropertiesAndLinks(nodeElement : Element, node : SNode, registry : SRootNodeRegistry) {
    const properties = nodeElement.children
    
    for(var property of childrenByTagName(nodeElement, "PROPERTY")) {
        const propertyRole = property.attributes.getNamedItem("role")!.value
        const propertyValue = property.attributes.getNamedItem("value")!.value
        const nodeProperty = registry.getPropertyByIndex(propertyRole)
        node.addProperty(nodeProperty, propertyValue)
    }
    //ToDo: handle references
}

function buildRootNodeRegistry(registryElement : Element) : SRootNodeRegistry {
    const sRootNodeRegistry = new SRootNodeRegistry();
    for(var languageRegistryElement of registryElement.getElementsByTagName("language")) {
        const languageId = languageRegistryElement?.attributes.getNamedItem("id")!.value
        const languageName = languageRegistryElement?.attributes.getNamedItem("name")!.value
        const myLanguage = SLanguageBuilder.getLanguage(languageName, languageId)
        const myLanguageRegistry = new SLanguageRegistry(myLanguage)
        sRootNodeRegistry.languages.push(myLanguageRegistry)
        for(var conceptRegistryElement of languageRegistryElement.getElementsByTagName("concept")) {
            const conceptId = conceptRegistryElement?.attributes.getNamedItem("id")!.value
            const conceptName = conceptRegistryElement?.attributes.getNamedItem("name")!.value

            const conceptFlag = conceptRegistryElement?.attributes.getNamedItem("flags")!.value
            const conceptIndex = conceptRegistryElement?.attributes.getNamedItem("index")!.value

            var myConcept = SLanguageBuilder.getConcept(myLanguage, conceptName, conceptId)
            const myConceptRegistry = new SConceptRegistry(myConcept, conceptFlag, conceptIndex)
            myLanguageRegistry.usedConcepts.push(myConceptRegistry)

            for(var linkRegistryElement of conceptRegistryElement.children) {
                
                const linkId = linkRegistryElement.attributes.getNamedItem("id")!.value
                const linkName = linkRegistryElement.attributes.getNamedItem("name")!.value
                const linkIndex = linkRegistryElement.attributes.getNamedItem("index")!.value
                    
                if (linkRegistryElement.tagName == "PROPERTY") {
                    const property = SLanguageBuilder.getProperty(myConcept, linkName, linkId)
                    const myRegistryProperty = new SPropertyRegistry(property, linkIndex)
                    myConceptRegistry.propertiesRegistries.push(myRegistryProperty)
                } else {
                    var link : SAbstractConceptLink;
                    if (linkRegistryElement.tagName == "CHILD") {
                        link = SLanguageBuilder.getChildLink(myConcept, linkName, linkId)
                    } else {
                        link = SLanguageBuilder.getReferenceLink(myConcept, linkName, linkId)
                    }
                    const myRegistryLink = new SLinkRegistry(link, linkIndex)
                    myConceptRegistry.linksRegistries.push(myRegistryLink)    
                }                
            }
        }
    }
    return sRootNodeRegistry;
}
