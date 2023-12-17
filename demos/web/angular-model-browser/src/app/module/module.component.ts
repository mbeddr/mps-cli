import { Component, Input } from '@angular/core';
import { SAbstractModule } from '../../../../../mps-cli-ts/src/model/smodule'
import { NgFor, NgForOf } from '@angular/common';

@Component({
  selector: 'app-module',
  standalone: true,
  imports: [ NgForOf ],
  templateUrl: './module.component.html',
  styleUrl: './module.component.css'
})
export class ModuleComponent {
  @Input() module! : SAbstractModule;
  
}
