## MPS CLI Python Library

This project provides a Python library which parses MPS files and builds the object model.

### Features
The following features are available:
- load MPS files (*.mpsr, *.mps, *.jar) and expose their content as Python object model 
  - solutions, models, root nodes, nodes, children, references, properties
- extract the meta-information and expose it as Python object model
  - list of languages, their concepts with information about properties, references, children

The core of the Python object model is given by the following classes:
- `SNode` - represents a node
- `SModel` - represents a model
- `SSolution` - represents a solution
- `SRepository` - the repository containing the parsed model and meta-information

### Limitations
The plugin has currently the following limitations:
- the recovered language information reflects only the used language in the loaded solutions

### Run tests

- `cd mps-cli-py`
- `python -m unittest discover`

### Build and upload to pypi.org

- `increae version number`
- `python3 -m build`
- `python3 -m twine upload dist/*`