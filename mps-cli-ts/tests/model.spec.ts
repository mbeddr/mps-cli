
import { SModel } from '../src/model/smodel';
import { parseModelHeader } from '../src/model/builder/model_builder';
import { parseXml } from '../src/file_parser';

import { assert } from "chai";

describe('testing parsing the model header', () => {
  it('model header', () => {

    const xmlStr = `<?xml version="1.0" encoding="UTF-8"?>
                    <model ref="r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed(mps.cli.lanuse.library_top.authors_top)" content="header">
                      <persistence version="9" />
                      <attribute name="content" value="header" />
                      <languages>
                        <use id="a7aaae55-aa5e-4a05-b2d0-013745658efa" name="mps.cli.landefs.people" version="0" />
                      </languages>
                      <imports />
                    </model>`;
    const doc : XMLDocument = parseXml(xmlStr);               
    const model : SModel = parseModelHeader(doc)
    assert.equal(model.name, "mps.cli.lanuse.library_top.authors_top")
    assert.equal(model.id, "r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed")

    const usedLan = model.usedLanguages
    assert.equal(usedLan.length, 1)
    assert.equal(usedLan[0].id, "a7aaae55-aa5e-4a05-b2d0-013745658efa")
    assert.equal(usedLan[0].name, "mps.cli.landefs.people")
  });
});