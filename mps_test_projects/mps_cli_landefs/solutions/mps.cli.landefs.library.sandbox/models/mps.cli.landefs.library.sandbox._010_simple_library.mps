<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:30f3da59-b3ae-4446-b16a-7d6f07d621cd(mps.cli.landefs.library.sandbox._010_simple_library)">
  <persistence version="9" />
  <languages>
    <use id="53fdadc6-a07c-4398-b66b-c9af1071186c" name="mps.cli.landefs.library" version="-1" />
    <use id="a7aaae55-aa5e-4a05-b2d0-013745658efa" name="mps.cli.landefs.people" version="0" />
  </languages>
  <imports />
  <registry>
    <language id="53fdadc6-a07c-4398-b66b-c9af1071186c" name="mps.cli.landefs.library">
      <concept id="5731700211659966675" name="mps.cli.landefs.library.structure.Library" flags="ng" index="3czhSE">
        <child id="5731700211660029142" name="entities" index="3czuCJ" />
      </concept>
      <concept id="5731700211659966677" name="mps.cli.landefs.library.structure.LibraryEntityBase" flags="ng" index="3czhSG">
        <property id="5731700211659966681" name="isbn" index="3czhSw" />
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
      <concept id="5731700211660036618" name="mps.cli.landefs.people.structure.PersonsContainer" flags="ng" index="3cz0NN">
        <child id="5731700211660036624" name="persons" index="3cz0ND" />
      </concept>
      <concept id="5731700211660036621" name="mps.cli.landefs.people.structure.Person" flags="ng" index="3cz0NO" />
    </language>
  </registry>
  <node concept="3czhSE" id="4Yb5JA31JJx">
    <property role="TrG5h" value="first_library" />
    <node concept="3czhSI" id="4Yb5JA31LBZ" role="3czuCJ">
      <property role="TrG5h" value="Tom Sawyer" />
      <property role="3czhSw" value="4325436" />
      <property role="3czhSy" value="1876" />
      <node concept="3cz0NE" id="4Yb5JA31NU8" role="3cz2VL">
        <ref role="3cz0NH" node="4Yb5JA31Nw6" resolve="Mark Twain" />
      </node>
    </node>
  </node>
  <node concept="3cz0NN" id="4Yb5JA31Nw5">
    <property role="TrG5h" value="classical_authors" />
    <node concept="3cz0NO" id="4Yb5JA31Nw6" role="3cz0ND">
      <property role="TrG5h" value="Mark Twain" />
    </node>
  </node>
</model>

