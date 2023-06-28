package org.mps_cli.cone_of_influence

class GitFacade {

    static List<String> computeFilesWhichAreModifiedInCurrentBranch(String gitRepoLocation, String branchName) {

        Closure<String> standardAndErrorOutputOfCommand = { String... command ->
            def commandString = command.join(' ')

            def sout = new StringBuilder(), serr = new StringBuilder()
            println("Running command '$commandString'")
            def proc = command.execute([], new File(gitRepoLocation))
            proc.consumeProcessOutput(sout, serr)
            proc.waitForOrKill(5000)

            def errorString = serr.toString()
            if (errorString?.trim()) {
                println ("Error running command '$commandString'")
                println (">>>>>>>>>>>>")
                print(errorString)
                println ("<<<<<<<<<<<<")
            }

            sout.toString()
        }

        def mergeBase = standardAndErrorOutputOfCommand('git', 'merge-base', branchName, 'HEAD').trim()

        def differencesString = standardAndErrorOutputOfCommand('git', 'diff', '--name-only', mergeBase)
        def differences = differencesString.split('\n')

        println("Differences:")
        differences.each { println(it) }

        differences
    }
}
