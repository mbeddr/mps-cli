## MPS CLI Rust Library

This project provides a Rust library which parses MPS files and builds the object model.

### Features
The following features are available:
- load MPS files (*.mpsr, *.mps, *.jar) and expose their content as Rust object model 
  - solutions, models, root nodes, nodes, children, references, properties
- extract the meta-information and expose it as Rust object model
  - list of languages, their concepts with information about properties, references, children

The core of the Rust object model is given by the following structures
- `SNode` - represents a node
- `SModel` - represents a model
- `SSolution` - represents a solution
- `SRepository` - the repository containing the parsed model and meta-information

### Limitations
The library has currently the following limitations:
- the recovered language information reflects only the used language in the loaded solutions

### Run tests

- `cd mps-cli-rs`
- `cargo test`
