<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:cc2d69d9-c3a6-4146-af20-3e597378cd63(mps.cli.lanuse.library_second.default_persistency.library_top)">
  <persistence version="9" />
  <languages>
    <use id="53fdadc6-a07c-4398-b66b-c9af1071186c" name="mps.cli.landefs.library" version="0" />
  </languages>
  <imports>
    <import index="f14o" ref="r:ca00da79-915e-4bdb-9c30-11a341daf779(mps.cli.lanuse.library_top.default_persistency.authors_top)" />
  </imports>
  <registry>
    <language id="53fdadc6-a07c-4398-b66b-c9af1071186c" name="mps.cli.landefs.library">
      <concept id="5731700211659966675" name="mps.cli.landefs.library.structure.Library" flags="ng" index="3czhSE">
        <child id="5731700211660029142" name="entities" index="3czuCJ" />
      </concept>
      <concept id="5731700211659966677" name="mps.cli.landefs.library.structure.LibraryEntityBase" flags="ng" index="3czhSG">
        <property id="5731700211659966681" name="isbn" index="3czhSw" />
        <property id="5731700211659966682" name="available" index="3czhSz" />
      </concept>
      <concept id="5731700211659966679" name="mps.cli.landefs.library.structure.Book" flags="ng" index="3czhSI">
        <property id="5731700211659966683" name="publicationDate" index="3czhSy" />
        <child id="5731700211660044296" name="authors" index="3cz2VL" />
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ng" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
    <language id="a7aaae55-aa5e-4a05-b2d0-013745658efa" name="mps.cli.landefs.people">
      <concept id="5731700211660036627" name="mps.cli.landefs.people.structure.PersonRef" flags="ng" index="3cz0NE">
        <reference id="5731700211660036628" name="person" index="3cz0NH" />
      </concept>
    </language>
  </registry>
  <node concept="3czhSE" id="4Yb5JA31NUC">
    <property role="TrG5h" value="_library" />
    <node concept="3czhSI" id="4Yb5JA31NUF" role="3czuCJ">
      <property role="TrG5h" value="Tom Sawyer" />
      <property role="3czhSy" value="1876" />
      <property role="3czhSw" value="4323r2" />
      <property role="3czhSz" value="true" />
      <node concept="3cz0NE" id="4Yb5JA31NVC" role="3cz2VL">
        <ref role="3cz0NH" to="f14o:4Yb5JA31NUv" resolve="Mark Twain" />
      </node>
    </node>
  </node>
</model>

