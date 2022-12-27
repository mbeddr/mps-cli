<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:ca00da79-915e-4bdb-9c30-11a341daf779(mps.cli.lanuse.library_top.default_persistency.authors_top)">
  <persistence version="9" />
  <languages>
    <use id="a7aaae55-aa5e-4a05-b2d0-013745658efa" name="mps.cli.landefs.people" version="0" />
  </languages>
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
</model>

