<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:b0ac08e7-eb3c-4977-a1e5-eb55651f3457(mps.cli.lanuse.library_top.default_persistency.library_top)">
  <persistence version="9" />
  <languages>
    <use id="53fdadc6-a07c-4398-b66b-c9af1071186c" name="mps.cli.landefs.library" version="0" />
    <use id="a7aaae55-aa5e-4a05-b2d0-013745658efa" name="mps.cli.landefs.people" version="0" />
  </languages>
  <imports>
    <import index="f14o" ref="r:ca00da79-915e-4bdb-9c30-11a341daf779(mps.cli.lanuse.library_top.default_persistency.authors_top)" />
  </imports>
  <registry>
    <language id="53fdadc6-a07c-4398-b66b-c9af1071186c" name="mps.cli.landefs.library">
      <concept id="5731700211659966680" name="mps.cli.landefs.library.structure.Magazine" flags="ng" index="3czhSx">
        <property id="5731700211659966689" name="periodicity" index="3czhSo" />
      </concept>
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
    <property role="TrG5h" value="munich_library" />
    <node concept="3czhSI" id="4Yb5JA31NUF" role="3czuCJ">
      <property role="TrG5h" value="Tom Sawyer" />
      <property role="3czhSy" value="1876" />
      <property role="3czhSw" value="4323r2" />
      <property role="3czhSz" value="true" />
      <node concept="3cz0NE" id="4Yb5JA31NUI" role="3cz2VL">
        <ref role="3cz0NH" to="f14o:4Yb5JA31NUv" resolve="Mark Twain" />
      </node>
    </node>
    <node concept="3czhSI" id="4Yb5JA31NUO" role="3czuCJ">
      <property role="TrG5h" value="The Mysterious Island" />
      <property role="3czhSy" value="1875" />
      <property role="3czhSw" value="4323r3" />
      <property role="3czhSz" value="true" />
      <node concept="3cz0NE" id="4Yb5JA31NUP" role="3cz2VL">
        <ref role="3cz0NH" to="f14o:4Yb5JA31NUx" resolve="Jules Verne" />
      </node>
    </node>
    <node concept="3czhSI" id="4Yb5JA31NV4" role="3czuCJ">
      <property role="TrG5h" value="Five Weeks in Baloon" />
      <property role="3czhSy" value="1863" />
      <property role="3czhSw" value="4323r3" />
      <property role="3czhSz" value="true" />
      <node concept="3cz0NE" id="4Yb5JA31NV5" role="3cz2VL">
        <ref role="3cz0NH" to="f14o:4Yb5JA31NUx" resolve="Jules Verne" />
      </node>
    </node>
    <node concept="3czhSx" id="ST9rMmXyEN" role="3czuCJ">
      <property role="TrG5h" value="Der Spiegel" />
      <property role="3czhSo" value="4Yb5JA31wzt/WEEKLY" />
      <property role="3czhSw" value="34223" />
    </node>
  </node>
  <node concept="3czhSE" id="7mrGlczwUeR">
    <property role="TrG5h" value="schwabing library" />
  </node>
</model>

