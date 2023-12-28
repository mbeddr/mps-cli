import { Component, Input } from '@angular/core';
import { SNode } from '../../../../../../mps-cli-ts/src/model/snode';
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
    return Array.from(this.node!.links).filter(it => it instanceof SReferenceLink)
  }

  childrenKeys() {
    return Array.from(this.node!.links.keys()).filter(it => it instanceof SChildLink)
  }

  children(link : SChildLink) : SNode[] {
    let myChildren = this.node?.links.get(link)!;
    return myChildren.filter(it => it instanceof SNode) as SNode[]
  }

  //key! : SProperty;
  //value! : string;
}
