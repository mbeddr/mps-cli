import { SModel } from "./smodel";
import { SAbstractModule } from "./smodule";
import { SNode } from "./snode";


export class SRepository {
    name : string;
    modules : SAbstractModule[] = []

    constructor(name : string) {
        this.name = name;
    }

    getNodesWithPropertyAndValue(propertyName : string, propertyValue? : string) : SNode[] {
        const res : SNode[] = [];
        this.modules.forEach(module => {
            module.getNodes(undefined).forEach(node => {
                const propVal = node.getProperty(propertyName)
                if(typeof propertyValue === 'undefined' || propVal === propertyValue)
                    res.push(node)
            }); 
        })
        return res;
    }

    findModelById(modelId : string) : SModel | undefined {
        for(const crtModule of this.modules) {
            for(const crtModel of crtModule.models) {
                if (crtModel.id === modelId)
                    return crtModel
            }
        }
        return undefined;
    }


}

