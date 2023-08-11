package org.mps_cli.model

abstract class SModuleBase {
    String moduleId
    String pathToModuleFile
    List<SModel> models = []
    List<SModuleRef> dependencies = []

    def abstract String name();

    /**
     * The file can be accessed with the ZIP file system (JVM 11+, Groovy code):
     * <pre>
     *     URI uri = sModule.uriToModuleFileInJar();
     *     if (uri != null) {
     *          FileSystems.newFileSystem(uri, [:]).withCloseable { fileSystem ->
     *              println Path.of(uri)
     *          }
     *     }
     * </pre>
     *
     * @return URI to the module file inside the JAR file or null if the module file is not inside a JAR file.
     */
    URI getUriToModuleFileInJar() {
        if (pathToModuleFile.startsWith("jar:file:")) {
            URI.create(pathToModuleFile)
        } else null
    }
}
