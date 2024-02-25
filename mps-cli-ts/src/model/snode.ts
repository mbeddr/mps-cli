import { SAbstractConceptLink, SChildLink, SConcept, SProperty } from "./sconcept";
import { SLanguage } from "./slanguage";
import { SRepository } from "./srepository";

export class SNode {
    myConcept : SConcept;
    id : string;
    links : [SAbstractConceptLink, (SNode | SNodeRef)[]][] = []
    properties : [SProperty, string][] = []
    myParent : SNode | undefined;

    constructor(myConcept : SConcept, id : string, parent : SNode | undefined) {
        this.myConcept = myConcept;
        this.id = id;
        this.myParent = parent
    }

    addLink(link : SAbstractConceptLink, node : SNode | SNodeRef) {
        var nodesForLink = this.links.find(it => it[0] === link);
        if (nodesForLink == undefined) {
            this.links.push([link, [node]])
        } else {
            nodesForLink[1].push(node)
        }
    }

    allLinkedNodes() : (SNode | SNodeRef)[] {
        var res : (SNode | SNodeRef)[] = []
        this.links.forEach(it => {
            res = res.concat(it[1])
        })
        return res
    }

    allLinks() : SAbstractConceptLink[] {
        return this.links.map(it => it[0])
    }

    addProperty(property : SProperty, value : string) {
        this.properties.push([property, value]);
    }

    getProperty(propertyName : string) : string | undefined {
        for(const prop of this.properties)
            if(prop[0].name === propertyName) 
                return prop[1];
        return undefined
    }

    descendants(concept : undefined | SConcept, includeSelf : boolean) : SNode[] {
        const res : SNode[] = []
        if (includeSelf && (concept === undefined || this.myConcept == concept)) { res.push(this) }

        const linksToVisit : [SChildLink, SNode[]][] = []
        const myChildren = Array.from(this.links).filter(it => it[0] instanceof SChildLink)
        myChildren.forEach(it => linksToVisit.push(it as [SChildLink, SNode[]]))

        while(linksToVisit.length > 0) {
            const crtLink = linksToVisit.pop()!
            res.push(...crtLink?.[1])

            for(const childNode of crtLink?.[1]) {
                const myChildren = childNode.links.filter(it => it[0] instanceof SChildLink)
                myChildren.forEach(it => linksToVisit.push(it as [SChildLink, SNode[]]))
            }
        }
        return res
    }

    getLinkedNodes(linkName : string) : (SNode | SNodeRef)[] {
        const res : (SNode | SNodeRef)[] = []
        this.links.forEach(it => {
            if (it[0].name === linkName) {
                res.push(...it[1])
            }    
        });
        return res
    }
}

export class SRootNode extends SNode {
    imports : SRootNodeImports | undefined;
    registry : SRootNodeRegistry | undefined;

    constructor(imports : SRootNodeImports | undefined, registry : SRootNodeRegistry | undefined, myConcept : SConcept, id : string) {
        super(myConcept, id, undefined);
        this.imports = imports
        this.registry = registry;
    }
}

export class SNodeRef {
    modelId : string
    nodeId : string
    resolveInfo : string;

    constructor(modelId : string, nodeId : string, resolveInfo : string) {
        this.modelId = modelId
        this.nodeId = nodeId
        this.resolveInfo = resolveInfo
    }

    resolve(repo : SRepository) : SNode | undefined {
        const myModel = repo.findModelById(this.modelId)
        if (myModel === undefined)
            return undefined;
        return myModel.findNodeById(this.nodeId)
    }
}

export class SRootNodeImports {
    imports : SModelImport[] = []

    getModelIdByIndex(index : string) : string {
        for(const imp of this.imports) {
            if (imp.myModelIndex === index)
                return imp.myModelId
        }
        //ToDo: fixme - handle the case when not found
        return "undefined";
    }

    getModelIndexByModelId(modelId : string) : string {
        for(const imp of this.imports) {
            if (imp.myModelId === modelId)
                return imp.myModelIndex
        }
        return "undefined";
    }

}

export class SRootNodeRegistry {
    languages : SLanguageRegistry[] = [];

    index2concepts : Map<string, SConcept> = new Map<string, SConcept>();
    index2links : Map<string, SAbstractConceptLink> = new Map<string, SAbstractConceptLink>();
    index2properties : Map<string, SProperty> = new Map<string, SProperty>();

    getConceptByIndex(index : string) : SConcept {
        return this.index2concepts.get(index)!;
    }

    getIndexForConcept(concept : SConcept) : string | undefined {
        for(const entry of this.index2concepts.entries())
            if(entry[1] === concept)
                return entry[0]
        return undefined;
    }

    getLinkByIndex(index : string) : SAbstractConceptLink {
        return this.index2links.get(index)!;
    }

    getIndexForLink(link : SAbstractConceptLink) : string | undefined {
        for(const entry of this.index2links.entries())
            if(entry[1] === link)
                return entry[0]
        return undefined;
    }

    getPropertyByRole(index : string) : SProperty {
        return this.index2properties.get(index)!;
    }

    getRoleForProperty(property : SProperty) : string | undefined {
        for(const entry of this.index2properties.entries())
            if(entry[1] === property)
                return entry[0]
        return undefined;
    }
}

export class SModelImport {
    myModelIndex : string
    myModelId : string
    myModelName : string
    implicit : boolean

    constructor(modelIndex : string, modelId : string, modelName : string, implicit : boolean) {
        this.myModelIndex = modelIndex
        this.myModelId = modelId
        this.myModelName = modelName
        this.implicit = implicit
    }
}

export class SLanguageRegistry {
    language : SLanguage;
    usedConcepts : SConceptRegistry[] = [];

    constructor(language : SLanguage) {
        this.language = language;
    }
}

export class SConceptRegistry {
    myConcept : SConcept;
    myConceptFlag : string
    myConceptIndex : string
    linksRegistries : SLinkRegistry[] = []
    propertiesRegistries : SPropertyRegistry[] = []

    constructor(myConcept : SConcept, myConceptFlag : string, myConceptIndex : string) {
        this.myConcept = myConcept;
        this.myConceptFlag = myConceptFlag;
        this.myConceptIndex = myConceptIndex;
    }
}

export class SLinkRegistry {
    link : SAbstractConceptLink;
    index : string;

    constructor(link : SAbstractConceptLink, index : string) {
        this.link = link
        this.index = index
    }
}

export class SPropertyRegistry {
    property : SProperty;
    index : string;

    constructor(property : SAbstractConceptLink, index : string) {
        this.property = property
        this.index = index
    }
}