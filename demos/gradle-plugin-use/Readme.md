## MPS CLI Gradle Plugin - Demo Project

This project demonstrates the use of the MPS CLI Gradle plugin.

[build.gradle](build.gradle) contains the task `buildModel` which builds the object model based on the parsed MPS files.


The object model is then used in `printModelInfo` which prints relevant information from the parsed files. We demonstrate: 
- how to access the model, 
- find nodes by concept, 
- access properties of nodes.

### Limitations

Limitations are documented [here](./../../mps-cli-gradle-plugin/Readme.md).
