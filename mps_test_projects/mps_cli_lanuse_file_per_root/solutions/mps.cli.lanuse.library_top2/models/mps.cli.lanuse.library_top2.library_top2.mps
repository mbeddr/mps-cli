<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:f8a8a42d-b216-41ed-8439-aea5147b2ac3(mps.cli.lanuse.library_top2.library_top2)">
  <persistence version="9" />
  <languages>
    <use id="53fdadc6-a07c-4398-b66b-c9af1071186c" name="mps.cli.landefs.library" version="0" />
  </languages>
  <imports />
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
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ng" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
  </registry>
  <node concept="3czhSE" id="3Lf5igFeP0">
    <property role="TrG5h" value="munich_library_2" />
    <node concept="3czhSx" id="3Lf5igFeP1" role="3czuCJ">
      <property role="TrG5h" value="Nature" />
      <property role="3czhSo" value="4Yb5JA31wzv/MONTHLY" />
      <property role="3czhSw" value="342342" />
    </node>
  </node>
</model>

