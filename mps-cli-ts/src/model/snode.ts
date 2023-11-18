import { SAbstractConceptLink, SChildLink, SConcept, SProperty } from "./sconcept";
import { SLanguage } from "./slanguage";
import { SRepository } from "./srepository";

export class SNode {
    myConcept : SConcept;
    id : string;
    links : Map<SAbstractConceptLink, (SNode | SNodeRef)[]> = new Map<SAbstractConceptLink, (SNode | SNodeRef)[]>
    properties : Map<SProperty, string> = new Map<SProperty, string>
    myParent : SNode | undefined;

    constructor(myConcept : SConcept, id : string, parent : SNode | undefined) {
        this.myConcept = myConcept;
        this.id = id;
        this.myParent = parent
    }

    addLink(link : SAbstractConceptLink, node : SNode | SNodeRef) {
        var nodesForLink = this.links.get(link);
        if (nodesForLink == null) {
            nodesForLink = [];
            this.links.set(link, nodesForLink)
        }
        nodesForLink.push(node)
    }

    allLinkedNodes() : (SNode | SNodeRef)[] {
        var res : (SNode | SNodeRef)[] = []
        this.links.forEach((linkedNodes : (SNode | SNodeRef)[], link : SAbstractConceptLink) => {
            res = res.concat(linkedNodes)
        })
        return res
    }

    addProperty(property : SProperty, value : string) {
        this.properties.set(property, value);
    }

    getProperty(propertyName : string) : string | undefined {
        for(const prop of this.properties.keys())
            if(prop.name === propertyName) 
                return this.properties.get(prop);
        return undefined
    }

    descendants(concept : undefined | SConcept, includeSelf : boolean) : SNode[] {
        const res : SNode[] = []
        if (includeSelf && (concept === undefined || this.myConcept == concept)) res.push(this)
        this.links.forEach((linkedNodes : (SNode | SNodeRef)[], link : SAbstractConceptLink) => {
            if (link instanceof SChildLink) {
                linkedNodes.forEach(it => {
                    const tmp = (it as SNode).descendants(concept, true)
                    res.push(...tmp)
                })
            }    
        });
        return res
    }

    getLinkedNodes(linkName : string) : (SNode | SNodeRef)[] {
        const res : (SNode | SNodeRef)[] = []
        this.links.forEach((linkedNodes : (SNode | SNodeRef)[], link : SAbstractConceptLink) => {
            if (link.name === linkName) {
                res.push(...linkedNodes)
            }    
        });
        return res
    }
}

export class SRootNode extends SNode {
    imports : SRootNodeImports
    registry : SRootNodeRegistry;

    constructor(imports : SRootNodeImports, registry : SRootNodeRegistry, myConcept : SConcept, id : string) {
        super(myConcept, id, undefined);
        this.imports = imports
        this.registry = registry;
    }
}

export class SNodeRef {
    modelId : string
    nodeId : string

    constructor(modelId : string, nodeId : string) {
        this.modelId = modelId
        this.nodeId = nodeId
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

}

export class SRootNodeRegistry {
    languages : SLanguageRegistry[] = [];

    index2concepts : Map<string, SConcept> = new Map<string, SConcept>();
    index2links : Map<string, SAbstractConceptLink> = new Map<string, SAbstractConceptLink>();
    index2properties : Map<string, SProperty> = new Map<string, SProperty>();

    getConceptByIndex(index : string) : SConcept {
        return this.index2concepts.get(index)!;
    }

    getLinkByIndex(index : string) : SAbstractConceptLink {
        return this.index2links.get(index)!;
    }

    getPropertyByIndex(index : string) : SProperty {
        return this.index2properties.get(index)!;
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