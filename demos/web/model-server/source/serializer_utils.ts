import { SChildLink, SConcept, SProperty, SReferenceLink } from "../../../../mps-cli-ts/src/model/sconcept";
import { SNode, SNodeRef, SRootNode } from "../../../../mps-cli-ts/src/model/snode";

function replacer(key : any, value : any) {
    if(value instanceof Map) {
      return {
        dataType: 'Map',
        value: Array.from(value.entries()), // or with spread: value: [...value]
      };
    } else {
      return value;
    }
  }

  function reviver(key : any, value : any) {
    if(typeof value === 'object' && value !== null) {
      if (value.dataType === 'Map') {
        return new Map(value.value);
      }
    }
    return value;
  }


  function removeCycles(node : SNode) : void {
    node.myParent = undefined;
    node.links.forEach((value, key) => {
      value.forEach(it => {
        if (it instanceof SNode) {
          removeCycles(it);
        }
      });
    })
  }
    

  function createProperObject(node : SRootNode) : SRootNode {
    let res = new SRootNode(undefined, undefined, node.myConcept, node.id)
    populateProperNode(node, res)
    return res;
  }

  function populateProperNode(node : SNode, properNode : SNode) {
    node.properties.forEach((value, key) => { properNode.properties.set(new SProperty(key.name, key.id), value) });

    node.links.forEach((value, key) => {
      if ((value[0] as SNodeRef).modelId != undefined) {
        // we have reference links
        let newValues = value.map(it => { return new SNodeRef((it as SNodeRef).modelId, (it as SNodeRef).nodeId)})
        properNode.links.set(new SReferenceLink(key.name, key.id), newValues)
      } else {
        // we have containment links
        let newChildren : SNode[] = value.map(it => {
          let fakeNode = it as SNode; 
          let newNode = new SNode(new SConcept(fakeNode.myConcept.name, fakeNode.myConcept.id), fakeNode.id, properNode)
          populateProperNode(fakeNode, newNode)
          return newNode
        })
        properNode.links.set(new SChildLink(key.name, key.id), newChildren)
      }
    });
  }

  export {replacer, reviver, removeCycles, createProperObject}