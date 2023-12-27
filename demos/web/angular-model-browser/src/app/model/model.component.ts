import { Component, Input } from '@angular/core';
import { SModel } from '../../../../../../mps-cli-ts/src/model/smodel';

@Component({
  selector: 'app-model',
  standalone: true,
  imports: [],
  templateUrl: './model.component.html',
})
export class ModelComponent {
  @Input() model! : SModel;

  
}
