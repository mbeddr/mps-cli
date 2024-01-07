
import { assert } from 'chai'
import { readdirSync, readFileSync, lstatSync } from 'fs'
import { loadSolutions, parseXml } from '../src/file_parser';
import { buildRootNode } from '../src/model/builder/root_node_builder';
import { SModel } from '../src/model/smodel';
import { SRootNode } from '../src/model/snode';
import { SRepository } from '../src/model/srepository';
import { serialize_root_node } from '../src/model/serializer/root_node_serializer';


describe('testing serializing the root node', () => {

    const projectPath = "../mps_test_projects/mps_cli_lanuse_file_per_root"
    const repo: SRepository = loadSolutions(projectPath);
    const library_second_library_top_model = repo.findModelsByName("mps.cli.lanuse.library_second.library_top")[0] 
    const library_top_library_top_model = repo.findModelsByName("mps.cli.lanuse.library_top.library_top")[0] 
    const library_top_authors_top_model = repo.findModelsByName("mps.cli.lanuse.library_top.authors_top")[0] 
    
    it('serialize _library root node', () => {
        const library = library_second_library_top_model.findRootNodesByName("_library")[0]
        const serializedLibrary = serialize_root_node(library_second_library_top_model, library)
        compare(projectPath + "/solutions/mps.cli.lanuse.library_second/models/mps.cli.lanuse.library_second.library_top/_library.mpsr", serializedLibrary)
    })

    it('serialize munich_library root node', () => {
        const munich_library = library_top_library_top_model.findRootNodesByName("munich_library")[0]
        const serializedLibrary = serialize_root_node(library_top_library_top_model, munich_library)
        compare(projectPath + "/solutions/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.library_top/munich_library.mpsr", serializedLibrary)
    })

    it('serialize schwabing_library root node', () => {
        const schwabing_library = library_top_library_top_model.findRootNodesByName("schwabing library")[0]
        const serializedLibrary = serialize_root_node(library_top_library_top_model, schwabing_library)
        compare(projectPath + "/solutions/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.library_top/schwabing library.mpsr", serializedLibrary)
    })

    it('serialize classical_authors root node', () => {
        const classical_authors = library_top_authors_top_model.findRootNodesByName("_010_classical_authors")[0]
        const serializedLibrary = serialize_root_node(library_top_authors_top_model, classical_authors)
        compare(projectPath + "/solutions/mps.cli.lanuse.library_top/models/mps.cli.lanuse.library_top.authors_top/_010_classical_authors.mpsr", serializedLibrary)
    })



}) 



function compare(filePathWithExpectedResult : string, serializedString : string) {
    const expectedString = readFileSync(filePathWithExpectedResult, 'utf8')
    const expectedLines = expectedString.split(/\r?\n/)
    const actualLines = serializedString.split(/\r?\n/)
    
    for(let i = 0; i < Math.min(expectedLines.length, actualLines.length); i++) {
        assert.equal(actualLines.at(i), expectedLines.at(i), `line ${i} is different`)
    }
    assert.equal(actualLines.length, expectedLines.length, `different number of lines:\n\texpected: ${expectedLines.length}\n\tactual: ${actualLines.length}`)
}