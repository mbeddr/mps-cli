import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { RepositoryComponent } from './repository/repository.component';
import { ModuleComponent } from './module/module.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RepositoryComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'angular-model-browser';

  repository = "C:\\work\\mps-cli\\mps_test_projects\\mps_cli_lanuse"
}
