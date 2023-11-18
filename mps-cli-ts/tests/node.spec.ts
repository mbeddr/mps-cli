
import { SModel } from '../src/model/smodel';
import { parseModelHeader } from '../src/model/builder/model_builder';
import { parseXml } from '../src/file_parser';

import { assert } from "chai";
import { buildRootNode } from '../src/model/builder/root_node_builder';
import { SRootNode } from '../src/model/snode';

describe('testing building of root nodes', () => {
  const xmlStr = `<?xml version="1.0" encoding="UTF-8"?>
                  <model ref="r:ec5f093b-9d83-43a1-9b41-b5952da8b1ed(mps.cli.lanuse.library_top.authors_top)" content="root">
                    <persistence version="9" />
                    <imports />
                    <registry>
                      <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
                        <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ng" index="TrEIO">
                          <property id="1169194664001" name="name" index="TrG5h" />
                        </concept>
                      </language>
                      <language id="a7aaae55-aa5e-4a05-b2d0-013745658efa" name="mps.cli.landefs.people">
                        <concept id="5731700211660036618" name="mps.cli.landefs.people.structure.PersonsContainer" flags="ng" index="3cz0NN">
                          <child id="5731700211660036624" name="persons" index="3cz0ND" />
                        </concept>
                        <concept id="5731700211660036621" name="mps.cli.landefs.people.structure.Person" flags="ng" index="3cz0NO" />
                      </language>
                    </registry>
                    <node concept="3cz0NN" id="4Yb5JA31NUu">
                      <property role="TrG5h" value="_010_classical_authors" />
                      <node concept="3cz0NO" id="4Yb5JA31NUv" role="3cz0ND">
                        <property role="TrG5h" value="Mark Twain" />
                      </node>
                      <node concept="3cz0NO" id="4Yb5JA31NUx" role="3cz0ND">
                        <property role="TrG5h" value="Jules Verne" />
                      </node>
                    </node>
                  </model>`;

  const doc : XMLDocument = parseXml(xmlStr);               
  const rootNode : SRootNode = buildRootNode(doc, new SModel("dummy_name", "dummy_id"))

  it('root node', () => {
    assert.equal(rootNode.myConcept.name, "mps.cli.landefs.people.structure.PersonsContainer")
    assert.equal(rootNode.id, "4Yb5JA31NUu")
    assert.equal(rootNode.allLinkedNodes().length, 2)
    assert.equal(rootNode.properties.size, 1)
    const propertiesKeysArray = Array.from(rootNode.properties.keys());

    const nameProperty = propertiesKeysArray[0]
    assert.equal(nameProperty.name, "name");
    assert.equal(nameProperty.id, "1169194664001");
    assert.equal(rootNode.properties.get(nameProperty), "_010_classical_authors");
    assert.equal(rootNode.getProperty("name"), "_010_classical_authors");

    const descendants = rootNode.descendants(undefined, false)
    assert.equal(descendants.length, 2)
    assert.equal(descendants[0].getProperty("name"), "Mark Twain")
  });
});