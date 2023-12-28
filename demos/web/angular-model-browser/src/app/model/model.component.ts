import { Component, Input } from '@angular/core';
import { SModel } from '../../../../../../mps-cli-ts/src/model/smodel';
import axios, { AxiosResponse } from 'axios';
import { SRootNode } from '../../../../../../mps-cli-ts/src/model/snode';
import { RootNodeComponent } from '../root-node/root-node.component';
import { NgForOf, NgIf } from '@angular/common';
import { createProperObject, reviver } from '../../../../model-server/source/serializer_utils';

@Component({
  selector: 'app-model',
  standalone: true,
  imports: [ NgForOf, NgIf, RootNodeComponent ],
  templateUrl: './model.component.html',
})
export class ModelComponent {
  @Input() model! : SModel;
  showRootsFlag : boolean = false;

  showRoots() {
    if (this.model.rootNodes.length == 0) {
      (async () => {
        let result: AxiosResponse = await axios.get(`http://localhost:6060/rootNodesOfModel/${this.model.id}`);
        let rootNodesAsFlatObjects : SRootNode[] = JSON.parse(result.data.message, reviver);  
  
        let rootNodes : SRootNode[] = rootNodesAsFlatObjects.map(it => {
          return createProperObject(it)
        })
  
        this.model.rootNodes = []
        this.model.rootNodes.push(...rootNodes)
      })()  
    }
    this.showRootsFlag = !this.showRootsFlag;
  }
}
