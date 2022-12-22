# MPS CLI Gradle Plugin - Demo Project

This project demonstrates the use of the MPS CLI Gradle plugin.
[build.gradle](build.gradle) contains the task "buildModel" which builds the object model based on the parsed MPS files 
(currently we support only MPS models saved using the File-per-Root persistency).

The object model is then used in "printModelInfo" which prints various information from the parsed files to demonstrate 
how to access the model, find nodes by concept, access properties of nodes.