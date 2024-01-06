import { JSDOM } from 'jsdom';
import { readdirSync, readFileSync, lstatSync } from 'fs'
import { join } from 'path'
import { parseModelHeader } from './model/builder/model_builder';
import { SModel } from './model/smodel';
import { SRootNode } from './model/snode';
import { buildRootNode } from './model/builder/root_node_builder';
import { SRepository } from './model/srepository';
import { buildSolution } from './model/builder/solution_builder';
import { SSolution } from './model/smodule';
import { XMLParser } from 'fast-xml-parser';
import { buildRootNodeFast } from './model/builder/root_node_builder_fast';

export function parseXml(str : string) : XMLDocument {
    const doc = new JSDOM("");
    const DOMParser = doc.window.DOMParser
    const parser = new DOMParser
    return parser.parseFromString(str, "text/xml");
}

export function loadModelsFromSolution(solutionDir : string) : SModel[] {
    const res : SModel[] = []
    try {
        console.log("Loading models from: " + solutionDir)
        const init = Date.now()
        const modelsDir = join(solutionDir, "models")
        const files = readdirSync(modelsDir);
        files.forEach(crtModelDir => {
            const filesOfModel = readdirSync(join(modelsDir, crtModelDir))
            const dotModelContent = readFileSync(join(modelsDir, crtModelDir, ".model"), 'utf8')
            const dotModelXMLDocument = parseXml(dotModelContent)
            const smodel : SModel = parseModelHeader(dotModelXMLDocument)
            res.push(smodel)
            filesOfModel.forEach(crtFile => {
                if (crtFile != ".model") {
                    let startRootNodeTime = performance.now()
                    const rootNodeString = readFileSync(join(modelsDir, crtModelDir, crtFile), 'utf8')
                                        
                    // >>>>>>>>>>>>> code below uses DOM parser
                    //const xmlDocument = parseXml(rootNodeString)
                    //const rootNode : SRootNode = buildRootNode(xmlDocument, smodel)
                    // <<<<<<<<<<<<<
                    
                    // >>>>>>>>>>>>> code below uses fast_xml_parser
                    const options = {
                        ignoreAttributes : false
                    };
                    const xmlJson = new XMLParser(options).parse(rootNodeString)
                    //console.log("Reading root node from file: " + crtFile + " " + (performance.now() - startRootNodeTime) + "ms")
                    const rootNode : SRootNode = buildRootNodeFast(xmlJson, smodel)
                    // <<<<<<<<<<<<<

                    smodel.rootNodes.push(rootNode)
                    //console.log("Building root node from file: " + crtFile + " " + (performance.now() - startRootNodeTime) + "ms")
                }
            })
        });
        console.log((Date.now() - init) + "ms for reading solution " + solutionDir)
      } catch (err) {
        console.error(err);
      }
    return res;  
}

export function loadSolutions(dir : string) : SRepository {
    const repo = new SRepository(dir)
    doLoadSolutions(dir, repo)
    return repo
}

function doLoadSolutions(dir : string, repo : SRepository) {
    try {
        const files = readdirSync(dir);
        const msdFile = files.find((it : string) => it.endsWith(".msd"))
        if (msdFile == undefined) {
            files.forEach(crtDir => {
                const fullName = join(dir, crtDir) 
                if (lstatSync(fullName).isDirectory()) {
                    doLoadSolutions(fullName, repo)
                }
            })
        } else {
            const msdFileContent = readFileSync(join(dir, msdFile), "utf8")
            const xmlDocument = parseXml(msdFileContent)
            const solution = buildSolution(xmlDocument)
            repo.modules.push(solution)
            const models : SModel[] = loadModelsFromSolution(dir)
            solution.models = models
        }
      } catch (err) {
        console.error(err);
      }
}