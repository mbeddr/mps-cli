package org.mps_cli.cone_of_influence

import org.mps_cli.PathUtils
import org.mps_cli.model.SModel
import org.mps_cli.model.SModuleBase
import org.mps_cli.model.SRepository

import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths

import static groovy.io.FileType.FILES

class Filesystem2SSolutionBridge {

    SRepository repository

    private static def modulePattern = ~/.*\.msd/
    private static def modelPattern = ~/.*\.mps|.*\.model/
    private static def moduleOrModelPattern = ~/$modulePattern|$modelPattern/

    class Result {
        boolean foundMissingModules = false
        Set<SModuleBase> modules = []
        boolean foundMissingModels = false
        Set<SModel> models = []

        private void registerModulePath(Path path) {
            if (Files.notExists(path)) {
                foundMissingModules = true
            } else {
                def realPath = PathUtils.pathToString(path)
                SModuleBase module = repository.findModuleByRealPath(realPath)

                if (module == null) {
                    foundMissingModules = true
                } else {
                    modules.add(module)
                }
            }
        }

        private void registerModelPath(Path path) {
            if (Files.notExists(path)) {
                foundMissingModels = true
            } else {
                def realPath = PathUtils.pathToString(path)
                SModel model = repository.findModelByRealPath(realPath)

                if (model == null) {
                    foundMissingModels = true
                } else {
                    models.add(model)
                }
            }
        }

        private void registerPath(Path path) {
            def filename = path.getFileName().toString()

            if (filename.matches(modulePattern)) {
                registerModulePath(path)
            } else if (filename.matches(modelPattern)) {
                registerModelPath(path)
            }
        }
    }

    Result computeModifiedEntities(
            String rootLocation,
            List<String> allModifiedFiles
    ) {
        def gitRepoLocation = Paths.get(rootLocation).toAbsolutePath().normalize()

        Result result = new Result()

        allModifiedFiles.each { file ->
            Path relativeFile = Paths.get(file)
            result.registerPath(gitRepoLocation.resolve(relativeFile))

            def relativeDirectory = relativeFile.parent
            while (relativeDirectory != null) {
                def absoluteDirectory = gitRepoLocation.resolve(relativeDirectory)
                if (Files.exists(absoluteDirectory)) {
                    absoluteDirectory.traverse(type: FILES, maxDepth: 0, nameFilter: moduleOrModelPattern) {
                        result.registerPath(it)
                    }
                }
                relativeDirectory = relativeDirectory.parent
            }
        }

        result
    }
}
