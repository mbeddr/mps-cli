import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { SNode, SRootNode } from '../../../../../../mps-cli-ts/src/model/snode';
import { EditorService } from '../editor.service';
import { Subscription } from 'rxjs';
import { NodeViewerComponent } from '../node-viewer/node-viewer.component';

@Component({
  selector: 'app-root-node-editor',
  standalone: true,
  imports: [ NodeViewerComponent ],
  templateUrl: './root-node-editor.component.html',
  styleUrl: './root-node-editor.component.css'
})
export class RootNodeEditorComponent implements OnInit, OnDestroy {

  viewedRootNode : SRootNode | undefined;
  subscription! : Subscription;
  
  constructor(public editorService : EditorService) {}

  ngOnInit() {
    this.subscription = this.editorService.currentRootNode.subscribe(rootNode => this.viewedRootNode = rootNode)
  }
  
  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

}
