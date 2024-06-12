import { Component, Input } from '@angular/core';
import { SNode, SNodeRef } from '../../../../../../mps-cli-ts/src/model/snode';
import { NgFor, NgIf } from '@angular/common';
import { SChildLink, SProperty, SReferenceLink } from '../../../../../../mps-cli-ts/src/model/sconcept';

@Component({
  selector: 'app-node-viewer',
  standalone: true,
  imports: [ NgFor, NgIf ],
  templateUrl: './node-viewer.component.html',
  styleUrl: './node-viewer.component.css'
})
export class NodeViewerComponent {
  @Input() node : SNode | undefined;

  propertiesKeys() {
    return Array.from(this.node!.properties)
  }

  referencesKeys() {
    return Array.from(this.node!.allLinks()).filter(it => it instanceof SReferenceLink)
  }

  references(link : SReferenceLink) : SNodeRef {
    return this.node!.getLinkedNodes(link.name)?.at(0) as SNodeRef;
  }

  childrenKeys() {
    return Array.from(this.node!.allLinks()).filter(it => it instanceof SChildLink)
  }

  children(link : SChildLink) : SNode[] {
    let myChildren = this.node?.getLinkedNodes(link.name)!;
    return myChildren.filter(it => it instanceof SNode) as SNode[]
  }

  //key! : SProperty;
  //value! : string;
}
