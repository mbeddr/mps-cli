

import { SAbstractConceptLink, SConcept, SProperty } from '../sconcept';
import { SModel } from '../smodel';
import { SConceptRegistry, SLanguageRegistry, SLinkRegistry, SModelImport, SNode, SNodeRef, SPropertyRegistry, SRootNode, SRootNodeImports, SRootNodeRegistry } from '../snode';
import { SLanguageBuilder } from './slanguage_builder';

export function buildRootNodeFast(json : any, smodel : SModel) : SRootNode {
    const model_json_element = (json as JsonElement)['model'];
    
    const registry_json_element = (model_json_element as JsonElement)['registry'] as JsonElement
    const registry = buildRootNodeRegistry(registry_json_element)
    
    const imports_json_element = (model_json_element as JsonElement)['imports'] as JsonElement;
    const imports = buildRootNodeImports(imports_json_element)

    const rootNode_json_element = (model_json_element as JsonElement)['node'] as JsonElement
    const rootNodeConceptIndex = rootNode_json_element["@_concept"] as string
    const rootNodeId = rootNode_json_element["@_id"] as string
    const rootNodeConcept = registry.getConceptByIndex(rootNodeConceptIndex)
    const mySRootNode = new SRootNode(imports, registry, rootNodeConcept, rootNodeId);

    populateNodePropertiesAndLinks(rootNode_json_element, mySRootNode, imports, registry, smodel)
    buildChildNodes(rootNode_json_element, mySRootNode, imports, registry, smodel)

    return mySRootNode
}


function buildChildNodes(parentNode_json_element : any, parent : SNode, imports : SRootNodeImports, registry : SRootNodeRegistry, smodel : SModel) {
    for(var node_json_element of ensure_array(parentNode_json_element["node"])) {
        const nodeConceptIndex = node_json_element["@_concept"] as string
        const nodeId = node_json_element["@_id"] as string
        const nodeConcept = registry.getConceptByIndex(nodeConceptIndex)
        const nodeRoleInParentString = node_json_element["@_role"] as string
        const linkInParent = registry.getLinkByIndex(nodeRoleInParentString)

        const node = new SNode(nodeConcept, nodeId, parent)
        parent.addLink(linkInParent, node)
        populateNodePropertiesAndLinks(node_json_element, node, imports, registry, smodel)

        buildChildNodes(node_json_element, node, imports, registry, smodel)
    }
}

function populateNodePropertiesAndLinks(node_json_element : any, node : SNode, imports : SRootNodeImports, registry : SRootNodeRegistry, smodel : SModel) {
    
    for(var property_json_element of  ensure_array(node_json_element["property"])) {
        const propertyRole = property_json_element["@_role"] as string
        const propertyValue = property_json_element["@_value"] as string
        const nodeProperty = registry.getPropertyByIndex(propertyRole)
        node.addProperty(nodeProperty, propertyValue)
    }

    for(var ref_json_element of  ensure_array(node_json_element["ref"])) {
        const refRole = ref_json_element["@_role"] as string

        var refNodeId : string;
        var modelId : string;
        if (ref_json_element["@_to"] != undefined) {
            const refTo = ref_json_element["@_to"] as string
            const refToParts = refTo.split(":")
            const refModel = refToParts[0]
            refNodeId = refToParts[1]
            modelId = imports.getModelIdByIndex(refModel)
        } else {
            modelId = smodel.id
            refNodeId = ref_json_element["@_node"] as string
        }
        const refLink = registry.getLinkByIndex(refRole)
        node.addLink(refLink, new SNodeRef(modelId, refNodeId))
    }

}


function buildRootNodeImports(imports_json_element : JsonElement) : SRootNodeImports {
    const imports = new SRootNodeImports
    for(var model_import_json_element of ensure_array(imports_json_element["import"])) {
        const importIndex = model_import_json_element["@_index"] as string
        const modelRef = model_import_json_element["@_ref"] as string
        const splits = modelRef.split("(")
        const modelId = splits[0]
        const modelName = splits[1].substring(0, splits[1].length)
        const implicit = model_import_json_element["@_implicit"] as string

        imports.imports.push(new SModelImport(importIndex, modelId, modelName, implicit === "true"))
    }
    return imports
}

function buildRootNodeRegistry(registry_json_element : JsonElement) : SRootNodeRegistry {
    const sRootNodeRegistry = new SRootNodeRegistry();
    
    for(var registry_language_json_element of ensure_array(registry_json_element["language"])) {
        const languageId = registry_language_json_element["@_id"] as string
        const languageName = registry_language_json_element["@_name"] as string
        const myLanguage = SLanguageBuilder.getLanguage(languageName, languageId)
        const myLanguageRegistry = new SLanguageRegistry(myLanguage)
        sRootNodeRegistry.languages.push(myLanguageRegistry)
        
        for(var registry_language_concept_json_element of ensure_array(registry_language_json_element["concept"])) {
            const conceptId = registry_language_concept_json_element["@_id"] as string
            const conceptName = registry_language_concept_json_element["@_name"] as string
            
            const conceptFlag = registry_language_concept_json_element["@_flag"] as string
            const conceptIndex = registry_language_concept_json_element["@_index"] as string
            
            var myConcept = SLanguageBuilder.getConcept(myLanguage, conceptName, conceptId)
            const myConceptRegistry = new SConceptRegistry(myConcept, conceptFlag, conceptIndex)
            myLanguageRegistry.usedConcepts.push(myConceptRegistry)
            sRootNodeRegistry.index2concepts.set(conceptIndex, myConcept)

            for(var registry_language_concept_property_json_element of ensure_array(registry_language_concept_json_element["property"])) {   
                const linkId = registry_language_concept_property_json_element["@_id"] as string
                const linkName = registry_language_concept_property_json_element["@_name"] as string
                const linkIndex = registry_language_concept_property_json_element["@_index"] as string
                    
                const property = SLanguageBuilder.getProperty(myConcept, linkName, linkId)
                const myRegistryProperty = new SPropertyRegistry(property, linkIndex)
                myConceptRegistry.propertiesRegistries.push(myRegistryProperty)
                sRootNodeRegistry.index2properties.set(linkIndex, property)
            }

            for(var registry_language_concept_child_json_element of ensure_array(registry_language_concept_json_element["child"])) {   
                const linkId = registry_language_concept_child_json_element["@_id"] as string
                const linkName = registry_language_concept_child_json_element["@_name"] as string
                const linkIndex = registry_language_concept_child_json_element["@_index"] as string
                    
                const link = SLanguageBuilder.getChildLink(myConcept, linkName, linkId)
                const myRegistryLink = new SLinkRegistry(link, linkIndex)
                myConceptRegistry.linksRegistries.push(myRegistryLink)    
                sRootNodeRegistry.index2links.set(linkIndex, link)
            }

            for(var registry_language_concept_reference_json_element of ensure_array(registry_language_concept_json_element["reference"])) {   
                const linkId = registry_language_concept_reference_json_element["@_id"] as string
                const linkName = registry_language_concept_reference_json_element["@_name"] as string
                const linkIndex = registry_language_concept_reference_json_element["@_index"] as string
                    
                const link = SLanguageBuilder.getReferenceLink(myConcept, linkName, linkId)
                const myRegistryLink = new SLinkRegistry(link, linkIndex)
                myConceptRegistry.linksRegistries.push(myRegistryLink)    
                sRootNodeRegistry.index2links.set(linkIndex, link)
            }
        }
    }
    return sRootNodeRegistry;
}

function ensure_array(obj : any) : JsonElement[] {
    if (obj === undefined) {
        return [];
    }
    if (Array.isArray(obj)) {
        return obj as JsonElement[]
    }
    return [obj as JsonElement]
}

interface JsonElement {
    [key: string]: JsonElement | JsonElement[] | string;
}