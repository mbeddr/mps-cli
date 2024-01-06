import { loadModelsFromSolution, loadSolutions, parseXml } from "../src/file_parser";

//const repo = loadSolutions("c:\\work\\E3_2.0_Solution\\solutions")
const repo = loadSolutions('C:\\work\\mbeddr.formal\\code\\tutorial-safety')
//console.log("starting..........")
//loadModelsFromSolution("C:\\work\\mps-cli\\mps_test_projects\\mps_cli_lanuse_file_per_root\\solutions\\mps.cli.lanuse.library_second")

console.log(`number of modules: ${ repo.modules.length }`)
console.log(`number of models: ${ repo.allModels().length }`)
console.log(`number of nodes: ${ repo.allNodes().length }`)