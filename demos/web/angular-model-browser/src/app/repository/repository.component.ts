import { Component } from '@angular/core';
import { ModuleComponent } from '../module/module.component';
import { SAbstractModule, SSolution } from '../../../../../mps-cli-ts/src/model/smodule';
import { loadSolutions } from '../../../../../mps-cli-ts/src/file_parser'
import { NgFor } from '@angular/common';

@Component({
  selector: 'app-repository',
  standalone: true,
  imports: [ ModuleComponent, NgFor ],
  templateUrl: './repository.component.html',
  styleUrl: './repository.component.css'
})
export class RepositoryComponent {
  modules : SAbstractModule[];

  constructor() {
    //var repo = loadSolutions("C:\\work\\mps-cli\\mps_test_projects\\mps_cli_lanuse");
    this.modules = []
    this.modules.push(new SSolution("dummy.solution_1", "dummy.id_1"), 
                      new SSolution("dummy.solution_2", "dummy.id_2"), )
  }
}
