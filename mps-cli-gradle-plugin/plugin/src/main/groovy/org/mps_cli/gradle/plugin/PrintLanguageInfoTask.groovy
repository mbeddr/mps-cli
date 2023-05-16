package org.mps_cli.gradle.plugin

import org.gradle.api.DefaultTask
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.TaskAction
import org.mps_cli.model.SRepository
import groovy.xml.MarkupBuilder

class PrintLanguageInfoTask extends DefaultTask {

    @Input
    String destinationDir;

    PrintLanguageInfoTask() {
        group "MPS-CLI"
        description "print information about the DSLs"
        dependsOn "buildModel"
    }


    @TaskAction
    def printLanguageInfo() {
        SRepository repo = project.buildModel.repository
        doPrintToHTML(repo)
    }

    def doPrintToHTML(SRepository repo) {
        def dir = new File(destinationDir).getAbsoluteFile().canonicalPath
        def languageInfoFile = new File(dir + File.separator + "language_info.html")
        println "language info saved to ${languageInfoFile.canonicalPath}"

        languageInfoFile.withWriter { w ->
            def mb = new MarkupBuilder(w)

            mb.html {
                head {
                    title: "Language Info"
                }
                body {
                    p "Language Info Extracted from: ${project.buildModel.sourcesDir.collect { new File(it).canonicalPath }}"
                    br()
                    br()

                    repo.languages.collect { lan ->
                        p(lan.name)
                        ul {
                            lan.concepts.collect { c ->
                               li {
                                   a(NAME: c.name) { mb.mkp.yield (c.shortName) }
                                   c.superConcepts.collect { sc ->
                                       a (HREF : "#" + sc.name) { mb.mkp.yield sc.shortName + " " }
                                   }
                               }
                               if (!c.properties.empty)
                                ul {
                                   li "Properties:"
                                   ul {
                                       c.properties.collect { li it }
                                   }
                                }
                               if (!c.children.empty)
                                 ul {
                                    li "Children:"
                                    ul {
                                        c.children.collect { li it }
                                    }
                                 }
                               if (!c.references.empty)
                                 ul {
                                   li "References:"
                                   ul {
                                     c.references.collect { li it }
                                   }
                                 }
                            }
                        }
                    }
                }
            }
        }

    }

}
