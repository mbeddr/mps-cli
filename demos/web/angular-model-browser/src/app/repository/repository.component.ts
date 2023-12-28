import { Component, Input } from '@angular/core';
import { ModuleComponent } from '../module/module.component';
import { SAbstractModule, SSolution } from '../../../../../../mps-cli-ts/src/model/smodule';
import { NgFor } from '@angular/common';
import axios, { AxiosResponse } from 'axios';
import { RootNodeEditorComponent } from '../root-node-editor/root-node-editor.component';

@Component({
  selector: 'app-repository',
  standalone: true,
  imports: [ ModuleComponent, NgFor, RootNodeEditorComponent ],
  templateUrl: './repository.component.html',
  styleUrl: './repository.component.css'
})
export class RepositoryComponent {
  modules : SAbstractModule[] = [];

  constructor() {
    (async () => {
      let result: AxiosResponse = await axios.get(`http://localhost:6060/solutions`);
      let solutions : SSolution[] = result.data.message;  

      this.modules = []
      this.modules.push(...solutions)
    })()
  }
}
