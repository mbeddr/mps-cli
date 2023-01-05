package org.mps_cli.cone_of_influence

class GitFacade {

    static List<String> computeFilesWhichAreDifferentFromBranch(gitRepoLocation, branchName) {
        def sout = new StringBuilder(), serr = new StringBuilder()
        def proc = "git diff --name-only $branchName".execute([], new File(gitRepoLocation))
        proc.consumeProcessOutput(sout, serr)
        proc.waitForOrKill(5000)

        def differences = sout.toString().split('\n')
        def differentFilesWithoutDeleted = differences.findAll {
            def absolutePath = gitRepoLocation + File.separator + it
            new File(absolutePath).exists()
        }
        differentFilesWithoutDeleted;
    }
}
