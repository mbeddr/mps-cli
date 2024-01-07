import { SModel } from "./smodel";
import { SAbstractModule } from "./smodule";
import { SNode, SRootNode } from "./snode";


export class SRepository {
    name : string;
    modules : SAbstractModule[] = []

    constructor(name : string) {
        this.name = name;
    }

    allNodes() : SNode[] {
        const res : SNode[] = []
        for(const crtModel of this.allModels()) {
            for(const crtNode of crtModel.getNodes(undefined)) {
                res.push(crtNode);
            }
        }
        return res;
    }

    getNodesWithPropertyAndValue(propertyName : string, propertyValue? : string) : SNode[] {
        const res : SNode[] = [];
        this.modules.forEach(module => {
            module.getNodes(undefined).forEach(node => {
                const propVal = node.getProperty(propertyName)
                if(propVal != undefined && (typeof propertyValue === 'undefined' || propVal === propertyValue))
                    res.push(node)
            });
        })
        return res;
    }

    findModuleById(moduleId : string) : SAbstractModule | undefined {
        for(const crtModule of this.modules) {
            if (crtModule.id === moduleId) {
                return crtModule;
            }
        }
        return undefined;
    }

    allModels() : SModel[] {
        const res : SModel[] = []
        for(const crtModule of this.modules) {
            res.push(...crtModule.models)
        }
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

    findModelsByName(modelName : string) : SModel[] {
        const res : SModel[] = []
        for(const crtModule of this.modules) {
            for(const crtModel of crtModule.models) {
                if (crtModel.name === modelName)
                    res.push(crtModel)
            }
        }
        return res;
    }

    findRootNodesByName(rootNodeName : string) : SRootNode[] {
        const res : SRootNode[] = []
        for(const crtModule of this.modules) {
            for(const crtModel of crtModule.models) {
                for(const crtRoot of crtModel.rootNodes) {
                    if (crtRoot.getProperty("name") === rootNodeName)
                        res.push(crtRoot)
                }
            }
        }
        return res;
    }

}

