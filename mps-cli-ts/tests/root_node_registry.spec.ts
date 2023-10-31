
import { SModel } from '../src/model/smodel';
import { parseModelHeader } from '../src/model/builder/model_builder';
import { parseXml } from '../src/file_parser';

import { assert } from "chai";
import { buildRootNode } from '../src/model/builder/root_node_builder';
import { SRootNode } from '../src/model/snode';

describe('testing parsing the root node registry', () => {
  it('registry information of root nodes', () => {

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
                    </node>
                  </model>`;
    const doc : XMLDocument = parseXml(xmlStr);               
    const rootNode : SRootNode = buildRootNode(doc)
    const rootNodeRegistry = rootNode.registry
    assert.equal(rootNodeRegistry.languages.length, 2)
    const jetbrains_mps_lang_core_registry = rootNodeRegistry.languages[0] 
    assert.equal(jetbrains_mps_lang_core_registry.language.name, "jetbrains.mps.lang.core")
    assert.equal(jetbrains_mps_lang_core_registry.usedConcepts.length, 1)

    const i_named_concept_registry = jetbrains_mps_lang_core_registry.usedConcepts[0]
    assert.equal(i_named_concept_registry.myConcept.name, "jetbrains.mps.lang.core.structure.INamedConcept")
    assert.equal(i_named_concept_registry.myConcept.id, "1169194658468")
    assert.equal(i_named_concept_registry.myConceptIndex, "TrEIO")

    const name_property_registry = i_named_concept_registry.propertiesRegistries[0]
    assert.equal(name_property_registry.property.name, "name")
    assert.equal(name_property_registry.property.id, "1169194664001")
    assert.equal(name_property_registry.index, "TrG5h")
  });
});