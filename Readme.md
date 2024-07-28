
## Command-Line-Interface (CLI) Tooling for Accessing MPS Models

This repository contains tooling for reading MPS models from command line - without having to start an MPS instance.

### Projects
- A Gradle plugin for reading MPS files and building an object model - [here](mps-cli-gradle-plugin/Readme.md).
- A Python library for reading MPS files and building an object model - [here](mps-cli-py/Readme.md).
- A Typescript libeary for reading MPS files and building an object model - [here](mps-cli-ts/Readme.md).

### Repository Structure
- `mps-cli-gradle-plugin` - the gradle plugin to read MPS models
- `mps-cli-py` - a Python library to read MPS models
- `mps-cli-ts` - a Typescript library to read MPS models 
- `mps-cli-ts` - a Rust library to read MPS models
- `demos` - examples for the use of the MPS-CLI tooling 
  - `gradle-plugin-use` - example of the use of the `mps-cli-gradle-plugin` 
  - `jupyter-notebook` - example of the use of the `mps-cli-py` library in a Jupyter Notebook
- `mps_test_projects` - MPS project containing language definitions and models used as test-data for the MPS-cli tools
