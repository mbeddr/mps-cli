## MPS CLI Python Library

This project provides a Python library which parses MPS files and builds the object model.

### Features
The following features are available:
- load MPS files (*.mpsr, *.mps, *.mpb, *.jar) and expose their content as Python object model 
  - solutions, models, root nodes, nodes, children, references, properties
- extract the meta-information and expose it as Python object model
  - list of languages, their concepts with information about properties, references, children

The core of the Python object model is given by the following classes:
- `SNode` - represents a node
- `SModel` - represents a model
- `SSolution` - represents a solution
- `SRepository` - the repository containing the parsed model and meta-information

### Create an MPS node reference URL

Use `create_node_reference_url` with the model UUID, model name, and node UUID from the parsed model. The URL points to `127.0.0.1:63342` by default; pass `port` to use another local MPS port.

```python
from mpscli.model.NodeReferenceUrl import create_node_reference_url

url = create_node_reference_url(model.uuid, model.name, node.uuid)
```

### Limitations
The library has currently the following limitations:
- the recovered language information reflects only the used language in the loaded solutions
  - if "mps/plugins" directory is considered the language information is loaded as an object model

### Run tests

- `cd mps-cli-py`
- `python -m unittest discover`

### Build and upload to pypi.org

#### Mac
- `increase version number`
- `python3 -m build`
- `python3 -m twine upload dist/*`

### Win
- `increase version number`
- `py -m build`
- `py -m twine upload dist/*`

To install build and twine:
- `py -m pip install --upgrade build`
- `py -m pip install --upgrade twine`