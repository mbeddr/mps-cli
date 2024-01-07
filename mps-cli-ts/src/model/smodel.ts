import { SConcept } from "./sconcept"
import { SLanguage } from "./slanguage"
import { SNode, SRootNode } from "./snode"

export class SModel {
    name : string
    id : string
    usedLanguages : SLanguage[]
    rootNodes : SRootNode[] = []

    constructor(name : string, id : string) {
        this.name = name
        this.id = id
        this.usedLanguages = []
    }

    getNodes(concept : SConcept | undefined) : SNode[] {
        const res : SNode[] = [];
        this.rootNodes.forEach(crtRoot => {
            res.push(...crtRoot.descendants(concept, true))
        });
        return res;
    }

    findNodeById(nodeId : string) : SNode | undefined {
        for(const crtNode of this.getNodes(undefined)) {
            if(crtNode.id === nodeId)
                return crtNode;
        }
        return undefined
    }

    findRootNodesByName(rootNodeName : string) : SRootNode[] {
        const res : SRootNode[] = []
        for(const crtNode of this.rootNodes) {
            if(crtNode.getProperty("name") === rootNodeName)
                res.push(crtNode)
        }
        return res
    }
}