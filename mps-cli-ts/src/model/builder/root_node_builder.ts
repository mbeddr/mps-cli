

import { SAbstractConceptLink, SConcept, SProperty } from '../sconcept';
import { SModel } from '../smodel';
import { SConceptRegistry, SLanguageRegistry, SLinkRegistry, SModelImport, SNode, SNodeRef, SPropertyRegistry, SRootNode, SRootNodeImports, SRootNodeRegistry } from '../snode';
import { SLanguageBuilder } from './slanguage_builder';
import { childrenByTagName, firstChildByTagName } from './utils';

export function buildRootNode(doc : Document, smodel : SModel) : SRootNode {
    const modelNode : Element = doc.getRootNode().firstChild as Element;
    const registryElement = firstChildByTagName(modelNode, "registry")!;
    const registry = buildRootNodeRegistry(registryElement)
    
    const importsElement = firstChildByTagName(modelNode, "imports")!;
    const imports = buildRootNodeImports(importsElement)

    const rootNodeElement = firstChildByTagName(modelNode, "node")!;
    const rootNodeConceptIndex = rootNodeElement.attributes.getNamedItem("concept")!.value
    const rootNodeId = rootNodeElement.attributes.getNamedItem("id")!.value
    const rootNodeConcept = registry.getConceptByIndex(rootNodeConceptIndex)
    const mySRootNode = new SRootNode(imports, registry, rootNodeConcept, rootNodeId);

    populateNodePropertiesAndLinks(rootNodeElement, mySRootNode, imports, registry, smodel)
    buildChildNodes(rootNodeElement, mySRootNode, imports, registry, smodel)

    return mySRootNode;
}


function buildChildNodes(parentNodeElement : Element, parent : SNode, imports : SRootNodeImports, registry : SRootNodeRegistry, smodel : SModel) {
    for(var nodeElement of childrenByTagName(parentNodeElement, "node")) {
        const nodeConceptIndex = nodeElement.attributes.getNamedItem("concept")!.value
        const nodeId = nodeElement.attributes.getNamedItem("id")!.value
        const nodeConcept = registry.getConceptByIndex(nodeConceptIndex)
        const nodeRoleInParentString = nodeElement.attributes.getNamedItem("role")!.value
        const linkInParent = registry.getLinkByIndex(nodeRoleInParentString)

        const node = new SNode(nodeConcept, nodeId, parent)
        parent.addLink(linkInParent, node)
        populateNodePropertiesAndLinks(nodeElement, node, imports, registry, smodel)

        buildChildNodes(nodeElement, node, imports, registry, smodel)
    }
}

function populateNodePropertiesAndLinks(nodeElement : Element, node : SNode, imports : SRootNodeImports, registry : SRootNodeRegistry, smodel : SModel) {
    
    for(var child of nodeElement.children) {
        if(child.tagName === "property") {
            let property = child
            const propertyRole = property.attributes.getNamedItem("role")!.value
            const propertyValue = property.attributes.getNamedItem("value")!.value
            const nodeProperty = registry.getPropertyByRole(propertyRole)
            node.addProperty(nodeProperty, propertyValue)
        } else if(child.tagName === "ref") {
            let ref = child
            const refRole = ref.attributes.getNamedItem("role")!.value
            const refResolveInfo = ref.attributes.getNamedItem("resolve")!.value

            var refNodeId : string;
            var modelId : string;
            if (ref.attributes.getNamedItem("to") != null) {
                const refTo = ref.attributes.getNamedItem("to")!.value
                const refToParts = refTo.split(":")
                const refModel = refToParts[0]
                refNodeId = refToParts[1]
                modelId = imports.getModelIdByIndex(refModel)
            } else {
                modelId = smodel.id
                refNodeId = ref.attributes.getNamedItem("node")!.value
            }
            const refLink = registry.getLinkByIndex(refRole)
            node.addLink(refLink, new SNodeRef(modelId, refNodeId, refResolveInfo))
        }
    }
}


function buildRootNodeImports(importsElement : Element) : SRootNodeImports {
    const imports = new SRootNodeImports
    for(var modelImportElement of childrenByTagName(importsElement, "import")) {
        const importIndex = modelImportElement?.attributes.getNamedItem("index")!.value
        const modelRef = modelImportElement?.attributes.getNamedItem("ref")!.value
        const splits = modelRef.split("(")
        const modelId = splits[0]
        const modelName = splits[1].substring(0, splits[1].length)
        const implicit = modelImportElement?.attributes.getNamedItem("implicit")!.value

        imports.imports.push(new SModelImport(importIndex, modelId, modelName, implicit === "true"))
    }
    return imports
}

function buildRootNodeRegistry(registryElement : Element) : SRootNodeRegistry {
    const sRootNodeRegistry = new SRootNodeRegistry();
    for(var languageRegistryElement of childrenByTagName(registryElement, "language")) {
        const languageId = languageRegistryElement?.attributes.getNamedItem("id")!.value
        const languageName = languageRegistryElement?.attributes.getNamedItem("name")!.value
        const myLanguage = SLanguageBuilder.getLanguage(languageName, languageId)
        const myLanguageRegistry = new SLanguageRegistry(myLanguage)
        sRootNodeRegistry.languages.push(myLanguageRegistry)
        for(var conceptRegistryElement of childrenByTagName(languageRegistryElement, "concept")) {
            const conceptId = conceptRegistryElement?.attributes.getNamedItem("id")!.value
            const conceptName = conceptRegistryElement?.attributes.getNamedItem("name")!.value

            const conceptFlag = conceptRegistryElement?.attributes.getNamedItem("flags")!.value
            const conceptIndex = conceptRegistryElement?.attributes.getNamedItem("index")!.value

            var myConcept = SLanguageBuilder.getConcept(myLanguage, conceptName, conceptId)
            const myConceptRegistry = new SConceptRegistry(myConcept, conceptFlag, conceptIndex)
            myLanguageRegistry.usedConcepts.push(myConceptRegistry)
            sRootNodeRegistry.index2concepts.set(conceptIndex, myConcept)

            for(var linkRegistryElement of conceptRegistryElement.children) {
                
                const linkId = linkRegistryElement.attributes.getNamedItem("id")!.value
                const linkName = linkRegistryElement.attributes.getNamedItem("name")!.value
                const linkIndex = linkRegistryElement.attributes.getNamedItem("index")!.value
                    
                if (linkRegistryElement.tagName == "property") {
                    const property = SLanguageBuilder.getProperty(myConcept, linkName, linkId)
                    const myRegistryProperty = new SPropertyRegistry(property, linkIndex)
                    myConceptRegistry.propertiesRegistries.push(myRegistryProperty)
                    sRootNodeRegistry.index2properties.set(linkIndex, property)
                } else {
                    var link : SAbstractConceptLink;
                    if (linkRegistryElement.tagName == "child") {
                        link = SLanguageBuilder.getChildLink(myConcept, linkName, linkId)
                    } else {
                        link = SLanguageBuilder.getReferenceLink(myConcept, linkName, linkId)
                    }
                    const myRegistryLink = new SLinkRegistry(link, linkIndex)
                    myConceptRegistry.linksRegistries.push(myRegistryLink)    
                    sRootNodeRegistry.index2links.set(linkIndex, link)
                }                
            }
        }
    }
    return sRootNodeRegistry;
}
