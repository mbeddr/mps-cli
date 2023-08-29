package org.mps_cli

import groovy.xml.XmlParser

import java.nio.file.FileSystems
import java.nio.file.Files
import java.nio.file.Path

class PathUtils {

    static Node parseXml(Path pathToXmlFile) {
        Files.newBufferedReader(pathToXmlFile).withCloseable { new XmlParser().parse(it) }
    }

    static String pathToString(Path path) {
        Files.notExists(path) ? null :
            path.getFileSystem() === FileSystems.default ? path.toRealPath().toString() :
            path.toUri().toString()
    }
}
