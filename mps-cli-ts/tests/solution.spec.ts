
import { SModel } from '../src/model/smodel';
import { parseModelHeader } from '../src/model/builder/model_builder';
import { parseXml } from '../src/file_parser';

import { assert } from "chai";
import { buildSolution } from '../src/model/builder/solution_builder';
import { SSolution } from '../src/model/smodule';

describe('testing parsing the solution', () => {
  it('solution', () => {

    const xmlStr = `<?xml version="1.0" encoding="UTF-8"?>
                    <solution name="mps.cli.lanuse.library_top" uuid="f1017d72-b2a4-4f19-9b27-1327f37f5b09" moduleVersion="0" compileInMPS="true">
                      <models>
                        <modelRoot contentPath="${module}" type="default">
                          <sourceRoot location="models" />
                        </modelRoot>
                      </models>
                      <facets>
                        <facet type="java">
                          <classes generated="true" path="${module}/classes_gen" />
                        </facet>
                      </facets>
                      <sourcePath />
                      <languageVersions>
                        <language slang="l:ceab5195-25ea-4f22-9b92-103b95ca8c0c:jetbrains.mps.lang.core" version="2" />
                        <language slang="l:53fdadc6-a07c-4398-b66b-c9af1071186c:mps.cli.landefs.library" version="0" />
                        <language slang="l:a7aaae55-aa5e-4a05-b2d0-013745658efa:mps.cli.landefs.people" version="0" />
                      </languageVersions>
                      <dependencyVersions>
                        <module reference="f1017d72-b2a4-4f19-9b27-1327f37f5b09(mps.cli.lanuse.library_top)" version="0" />
                      </dependencyVersions>
                    </solution>`;
    const doc : XMLDocument = parseXml(xmlStr);               
    const solution : SSolution = buildSolution(doc)
    assert.equal(solution.name, "mps.cli.lanuse.library_top")
    assert.equal(solution.id, "f1017d72-b2a4-4f19-9b27-1327f37f5b09")
  });
});