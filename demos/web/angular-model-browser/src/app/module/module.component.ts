import { Component, Input } from '@angular/core';
import { SAbstractModule, SSolution } from '../../../../../../mps-cli-ts/src/model/smodule'
import { NgIf, NgForOf } from '@angular/common';
import axios, { AxiosResponse } from 'axios';
import { SModel } from '../../../../../../mps-cli-ts/src/model/smodel';
import { ModelComponent } from '../model/model.component';


@Component({
  selector: 'app-module',
  standalone: true,
  imports: [ NgForOf, NgIf, ModelComponent ],
  templateUrl: './module.component.html',
  styleUrl: './module.component.css'
})
export class ModuleComponent {
  @Input() module! : SAbstractModule;
  showModelsFlag : boolean = false;
 
  showModels() {
    if (this.module.models.length == 0) {
      (async () => {
        if (this.module.models.length == 0) {
          let result: AxiosResponse = await axios.get(`http://localhost:6060/modelsOfSolution/${this.module.id}`);
          let models : SModel[] = result.data.message;  
          this.module.models.push(...models)
        }
      })()  
    }
    this.showModelsFlag = !this.showModelsFlag;
  }
}
