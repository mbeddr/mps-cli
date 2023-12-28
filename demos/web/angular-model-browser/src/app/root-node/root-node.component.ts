import { Component, Input } from '@angular/core';
import { SRootNode } from '../../../../../../mps-cli-ts/src/model/snode';
import { EditorService } from '../editor.service';

@Component({
  selector: 'app-root-node',
  standalone: true,
  imports: [],
  templateUrl: './root-node.component.html',
})
export class RootNodeComponent {
  @Input() rootNode! : SRootNode

  constructor(private editorService : EditorService) {}

  openRootNode() {
    this.editorService.changeRootNode(this.rootNode)
  }
}
