import { Injectable } from '@angular/core';
import { SRootNode } from '../../../../../mps-cli-ts/src/model/snode';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class EditorService {

  private rootNodeSource = new BehaviorSubject<SRootNode | undefined>(undefined);
  currentRootNode = this.rootNodeSource.asObservable();

  changeRootNode(rootNode : SRootNode) {
    this.rootNodeSource.next(rootNode)
  }
}
