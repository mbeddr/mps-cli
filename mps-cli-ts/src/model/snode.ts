import { SAbstractConceptLink, SConcept, SProperty } from "./sconcept";
import { SLanguage } from "./slanguage";

export class SNode {
    myConcept : SConcept;
    id : string;
    links : Map<SAbstractConceptLink, SNode[]> = new Map<SAbstractConceptLink, SNode[]>
    properties : Map<SProperty, string> = new Map<SProperty, string>
    myParent : SNode | undefined;

    constructor(myConcept : SConcept, id : string, parent : SNode | undefined) {
        this.myConcept = myConcept;
        this.id = id;
        this.myParent = parent
    }

    addLink(link : SAbstractConceptLink, node : SNode) {
        var nodesForLink = this.links.get(link);
        if (nodesForLink == null) {
            nodesForLink = [];
            this.links.set(link, nodesForLink)
        }
        nodesForLink.push(node)
    }

    allLinkedNodes() : SNode[] {
        var res : SNode[] = []
        this.links.forEach((linkedNodes : SNode[], link : SAbstractConceptLink) => {
            res = res.concat(linkedNodes)
        })
        return res
    }

    addProperty(property : SProperty, value : string) {
        this.properties.set(property, value);
    }
}

export class SRootNode extends SNode {
    registry : SRootNodeRegistry;

    constructor(registry : SRootNodeRegistry, myConcept : SConcept, id : string) {
        super(myConcept, id, undefined);
        this.registry = registry;
    }
}

export class SRootNodeRegistry {
    languages : SLanguageRegistry[] = [];

    private index2concepts : Map<string, SConcept> = new Map<string, SConcept>();
    private index2links : Map<string, SAbstractConceptLink> = new Map<string, SAbstractConceptLink>();
    private index2properties : Map<string, SProperty> = new Map<string, SProperty>();

    getConceptByIndex(index : string) : SConcept {
        if (this.index2concepts.size == 0) {
            for(var lan of this.languages) {
                for(var con of lan.usedConcepts) {
                    this.index2concepts.set(con.myConceptIndex, con.myConcept)
                }
            }                
        }
        return this.index2concepts.get(index)!;
    }

    getLinkByIndex(index : string) : SAbstractConceptLink {
        if (this.index2links.size == 0) {
            for(var lan of this.languages) {
                for(var con of lan.usedConcepts) {
                    for(var link of con.linksRegistries) {
                        this.index2links.set(link.index, link.link)
                    }    
                }
            }                
        }
        return this.index2links.get(index)!;
    }

    getPropertyByIndex(index : string) : SProperty {
        if (this.index2properties.size == 0) {
            for(var lan of this.languages) {
                for(var con of lan.usedConcepts) {
                    for(var property of con.propertiesRegistries) {
                        this.index2properties.set(property.index, property.property)
                    }    
                }
            }                
        }
        return this.index2properties.get(index)!;
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