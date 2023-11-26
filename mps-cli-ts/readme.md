# Typescript-based Loading of MPS Models

## Structure
- 'src' - source code
- 'tests' - unit tests

## Run Tests
- Run tests with: `npm test`

### Features
The following features are available:
- load MPS files (*.mpsr) and expose their content as Typescript object model 
  - solutions, models, root nodes, nodes, children, references, properties

The core of the Typescript object model is given by the following classes:
- `SNode` - represents a node
- `SModel` - represents a model
- `SSolution` - represents a solution
- `SRepository` - the repository containing the parsed model and meta-information

### Limitations
The plugin has currently the following limitations:
- only File-per-Root persistency is currently supported
- the recovered language information reflects only the used language in the loaded solutions