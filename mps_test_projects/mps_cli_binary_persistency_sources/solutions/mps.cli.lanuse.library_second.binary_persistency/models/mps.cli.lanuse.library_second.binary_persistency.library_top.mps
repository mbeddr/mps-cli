<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:314c3573-0151-4291-97da-f7861bc9a8c2(mps.cli.lanuse.library_second.binary_persistency.library_top)">
  <persistence version="9" />
  <languages>
    <use id="53fdadc6-a07c-4398-b66b-c9af1071186c" name="mps.cli.landefs.library" version="0" />
    <use id="a7aaae55-aa5e-4a05-b2d0-013745658efa" name="mps.cli.landefs.people" version="0" />
  </languages>
  <imports>
    <import index="np64" ref="r:cf91f372-8bfd-44b8-8e34-024eb23e64a8(mps.cli.lanuse.library_top.binary_persistency.authors_top)" />
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
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ngI" index="TrEIO">
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
        <ref role="3cz0NH" to="np64:4Yb5JA31NUv" resolve="Mark Twain" />
      </node>
    </node>
  </node>
</model>

