package org.mps_cli.model

class SModel {
    String name
    String modelId
    String pathToModelFile
    SModuleBase myModule
    boolean isFilePerRootPersistency
    boolean isDoNotGenerate
    List<SNode> rootNodes = []
    List<SModelRef> imports = []

    // caching
    List<SNode> allNodes = new ArrayList<>(1024)

    Map<String, SNode> nodeId2Node() {
        allNodes.collectEntries {[it.id, it] }
    }

    /**
     * The file can be accessed with the ZIP file system (JVM 11+, Groovy code):
     * <pre>
     *     URI uri = sModel.uriToModelFileInJar();
     *     if (uri != null) {
     *          FileSystems.newFileSystem(uri, [:]).withCloseable { fileSystem ->
     *              println Path.of(uri)
     *          }
     *     }
     * </pre>
     *
     * @return URI to the model file inside the JAR file or null if the model file is not inside a JAR file.
     */
    URI getUriToModelFileInJar() {
        if (pathToModelFile.startsWith("jar:file:")) {
            URI.create(pathToModelFile)
        } else null
    }
}
