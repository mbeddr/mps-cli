## MPS CLI Gradle Plugin

This project provides a Gradle plugin developed with Groovy which parses MPS files and builds the object model.

A demo about using the MPS CLI Gradle plugin is provided [here](../demos/gradle-plugin-use/Readme.md).

### Tasks
This Gradle plugin contributes the following tasks:
- `buildModel` builds the object model based on the MPS files from `sourcesDir` 
  - `sourcesDir`is a list with directories containing solutions
- `printLanguageInfo` prints the information about the languages in a file specified by `destinationDir`

### Features
The following features are available:
- load MPS files (*.mps, *.mpsr) including binary models as jars and expose their content as Groovy object model 
  - solutions, models, root nodes, nodes, children, references, properties
- extract the meta-information and expose it as Groovy object model
  - list of languages, their concepts with information about properties, references, children

The core of the Groovy object model is given by the following classes:
- `SNode` - represents a node
- `SModel` - represents a model
- `SSolution` - represents a solution
- `SRepository` - the repository containing the parsed model and meta-informations

### Limitations
The plugin has currently the following limitations:
- the extracted meta-information is based solely on the information saved in the model files
  - e.g. if a concept is not instantiated at all in the set of loaded models, the meta-information will not contain it at all
  - e.g. if a link of a concept is not set in any of its instances, the meta-information will not contain it at all
