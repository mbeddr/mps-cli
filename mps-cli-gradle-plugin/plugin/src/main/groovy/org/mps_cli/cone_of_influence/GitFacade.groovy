package org.mps_cli.cone_of_influence

import java.nio.file.Paths

class GitFacade {

    static List<String> computeFilesWhichAreModifiedInCurrentBranch(String gitRepoLocation, String branchName) {
        def absoluteGitRepoLocation = Paths.get(gitRepoLocation).toAbsolutePath().normalize().toFile()

        Closure<String> standardOutputOfCommand = { String... command ->
            def commandString = command.join(' ')

            def sout = new StringBuilder(), serr = new StringBuilder()
            println("Running command '$commandString'")
            def proc = command.execute([], absoluteGitRepoLocation)
            proc.consumeProcessOutput(sout, serr)
            proc.waitForOrKill(60000)

            if (proc.exitValue() != 0) {
                throw new RuntimeException(
                        """Error running command '$commandString' - 
                            process failed with exit code ${proc.exitValue()}""".stripIndent())
            }

            def errorString = serr.toString()
            if (errorString?.trim()) {
                throw new RuntimeException(
                        """Error running command '$commandString': 
                           $errorString""".stripIndent())
            }

            sout.toString()
        }

        def mergeBase = standardOutputOfCommand('git', 'merge-base', branchName, 'HEAD').trim()

        def differencesString = standardOutputOfCommand('git', 'diff', '--name-only', mergeBase)
        def differences = differencesString.split('\n')

        println(">>>>>>>>>>>>> Differences:")
        differences.each { println(it) }
        println ("<<<<<<<<<<<<")

        differences
    }
}
