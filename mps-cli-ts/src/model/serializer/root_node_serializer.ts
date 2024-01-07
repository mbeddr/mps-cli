import { childrenByTagName } from "../builder/utils";
import { SAbstractConceptLink, SChildLink, SProperty, SReferenceLink } from "../sconcept";
import { SModel } from "../smodel";
import { SNode, SNodeRef, SRootNode, SRootNodeImports, SRootNodeRegistry } from "../snode";


export function serialize_root_node(model : SModel, root_node : SRootNode) : string {
    var res = ""
    res += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + "\n"
    res += `<model ref="${model.id}(${model.name})" content="root">` + "\n"
    var PADDING = "  "
    res += PADDING + "<persistence version=\"9\" />" + "\n"
    
    res += serialize_imports(root_node, PADDING);
    res += serialize_registry(root_node, PADDING);
    res += serialize_nodes(root_node.registry!, root_node.imports!, root_node, undefined, PADDING);

    res += "</model>\n\n"
    return res;
}

function serialize_nodes(registry : SRootNodeRegistry, imports : SRootNodeImports, node : SNode, role : string | undefined, padding : string) : string {
    var res = role === undefined ? 
                    `${padding}<node concept="${registry.getIndexForConcept(node.myConcept)}" id="${node.id}">\n` : 
                    `${padding}<node concept="${registry.getIndexForConcept(node.myConcept)}" id="${node.id}" role="${role}">\n`
    padding = increase_indent(padding)
    
    for(const prop2Val of node.properties) {
        res += `${padding}<property role="${registry.getRoleForProperty(prop2Val[0])}" value="${prop2Val[1]}" />\n`
    }
    
    for(const refLink of node.links.filter(it => it[0] instanceof SReferenceLink)) {
        const refNode = (refLink[1][0] as SNodeRef)
        res += `${padding}<ref role="${registry.getIndexForLink(refLink[0])}" to="${imports.getModelIndexByModelId(refNode.modelId)}:${refNode.nodeId}" resolve="${refNode.resolveInfo}" />\n`
    }
    for(const childLink of node.links.filter(it => it[0] instanceof SChildLink)) {
        for(const child of childLink[1]!) {
            res += serialize_nodes(registry, imports, child as SNode, registry.getIndexForLink(childLink[0]), padding)
        }
    }
    padding = decrease_indent(padding)
    res += `${padding}</node>\n`
    return res;
}

function serialize_registry(root_node : SRootNode, padding : string) : string {
    var res = `${padding}<registry>\n`
    padding = increase_indent(padding)
    for(var languageRegistry of root_node.registry?.languages!) {
        res += `${padding}<language id="${languageRegistry.language.id}" name="${languageRegistry.language.name}">\n`
        padding = increase_indent(padding)
        for(var concept of languageRegistry.usedConcepts) {
            const noPropertiesAndLinks = concept.propertiesRegistries.length === 0 && concept.linksRegistries.length === 0 
            res += `${padding}<concept id="${concept.myConcept.id}" name="${concept.myConcept.name}" flags="${concept.myConceptFlag}" index="${concept.myConceptIndex}"${noPropertiesAndLinks ? " /" : ""}>\n`
            padding = increase_indent(padding)    
            for(var prop of concept.propertiesRegistries) {
                res += `${padding}<property id="${prop.property.id}" name="${prop.property.name}" index="${prop.index}" />\n`
            }
            padding = decrease_indent(padding)
            padding = increase_indent(padding)    
            for(var link of concept.linksRegistries) {
                const linkKind = link.link instanceof SChildLink ? "child" : "reference"
                res += `${padding}<${linkKind} id="${link.link.id}" name="${link.link.name}" index="${link.index}" />\n`
            }
            padding = decrease_indent(padding)
            if (!noPropertiesAndLinks) {
                res += `${padding}</concept>\n`
            }
        }
        padding = decrease_indent(padding)
        res += `${padding}</language>\n`
    }
    padding = decrease_indent(padding)
    res += `${padding}</registry>\n`

    return res;
}

function serialize_imports(root_node : SRootNode, padding : string) : string {
    if(root_node.imports?.imports.length == 0) {
        return padding + "<imports />\n"; 
    }
    
    var res = padding + "<imports>\n";
    padding = increase_indent(padding)
    for(var crtImport of root_node.imports?.imports!) {
        res += `${padding}<import index="${crtImport.myModelIndex}" ref="${crtImport.myModelId}(${crtImport.myModelName})" implicit="${crtImport.implicit}" />\n`
    }
    padding = decrease_indent(padding)
    res += `${padding}</imports>\n`
    return res;
}

function increase_indent(padding : string) : string {
    return padding + "  "
}

function decrease_indent(padding : string) : string {
    return padding.substring(2)
}