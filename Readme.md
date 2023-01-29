
## Command-Line-Interface (CLI) Tooling for Accessing MPS Models

This repository contains tooling for reading MPS models from command line - without having to start an MPS instance.

### Projects
- A Gradle plugin for reading MPS files and building an object model - [here](mps-cli-gradle-plugin/Readme.md).
- A Python library for reading MPS files and building an object model - [here](mps-cli-py/Readme.md).

### Repository Structure
- `mps-cli-gradle-plugin` - the gradle plugin project
- `mps-cli-py` - a Python library to parse MPS models
- `demos` - examples for the use of the MPS-CLI tooling 
  - `gradle-plugin-use` - example of the use of the `mps-cli-gradle-plugin` 
- `mps_test_projects` - MPS project containing language definitions and models used as test-data for the MPS-cli tools
