import { SConcept } from "./sconcept";
import { SModel } from "./smodel";
import { SNode } from "./snode";


export abstract class SAbstractModule {
    name : string;
    id : string;
    models : SModel[] = []

    constructor(name : string, id : string) {
        this.name = name;
        this.id = id
    }

    getNodes(concept : SConcept | undefined) : SNode[] {
        const res : SNode[] = []
        this.models.forEach((m : SModel) => {
            res.push(...m.getNodes(concept))
        })
        return res
    }

}

export class SSolution extends SAbstractModule {

    constructor(name : string, id : string) {
        super(name, id)
    }
}