package org.mps_cli.cone_of_influence

class GitFacade {

    static List<String> computeFilesWhichAreModifiedInCurrentBranch(gitRepoLocation, branchName) {
        def sout = new StringBuilder(), serr = new StringBuilder()
        def gitCommand = "git diff --name-only $branchName... --"
        println ("Running git command '$gitCommand'")
        def proc = gitCommand.execute([], new File(gitRepoLocation))
        proc.consumeProcessOutput(sout, serr)
        proc.waitForOrKill(5000)

        def differences = sout.toString().split('\n')

        if (serr.toString()?.trim()) {
            println ("Error while running git command '$gitCommand'")
            println (">>>>>>>>>>>>")
            print(serr.toString())
            println ("<<<<<<<<<<<<")
        }

        println("Differences:")
        differences.each {println(it) }

        differences
    }
}
