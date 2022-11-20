<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:642336b8-2013-4d3c-b365-176bd2494823(mps.cli.landefs.library.structure)">
  <persistence version="9" />
  <languages>
    <use id="c72da2b9-7cce-4447-8389-f407dc1158b7" name="jetbrains.mps.lang.structure" version="9" />
    <devkit ref="78434eb8-b0e5-444b-850d-e7c4ad2da9ab(jetbrains.mps.devkit.aspect.structure)" />
  </languages>
  <imports>
    <import index="xcst" ref="r:4f2aa5a4-cc51-472c-8f0c-9263938c8fe6(mps.cli.landefs.people.structure)" />
    <import index="tpck" ref="r:00000000-0000-4000-0000-011c89590288(jetbrains.mps.lang.core.structure)" implicit="true" />
  </imports>
  <registry>
    <language id="c72da2b9-7cce-4447-8389-f407dc1158b7" name="jetbrains.mps.lang.structure">
      <concept id="3348158742936976480" name="jetbrains.mps.lang.structure.structure.EnumerationMemberDeclaration" flags="ng" index="25R33">
        <property id="1421157252384165432" name="memberId" index="3tVfz5" />
      </concept>
      <concept id="3348158742936976479" name="jetbrains.mps.lang.structure.structure.EnumerationDeclaration" flags="ng" index="25R3W">
        <child id="3348158742936976577" name="members" index="25R1y" />
      </concept>
      <concept id="1082978164218" name="jetbrains.mps.lang.structure.structure.DataTypeDeclaration" flags="ng" index="AxPO6">
        <property id="7791109065626895363" name="datatypeId" index="3F6X1D" />
      </concept>
      <concept id="1169125787135" name="jetbrains.mps.lang.structure.structure.AbstractConceptDeclaration" flags="ig" index="PkWjJ">
        <property id="6714410169261853888" name="conceptId" index="EcuMT" />
        <property id="4628067390765956802" name="abstract" index="R5$K7" />
        <property id="5092175715804935370" name="conceptAlias" index="34LRSv" />
        <child id="1071489727083" name="linkDeclaration" index="1TKVEi" />
        <child id="1071489727084" name="propertyDeclaration" index="1TKVEl" />
      </concept>
      <concept id="1169127622168" name="jetbrains.mps.lang.structure.structure.InterfaceConceptReference" flags="ig" index="PrWs8">
        <reference id="1169127628841" name="intfc" index="PrY4T" />
      </concept>
      <concept id="1071489090640" name="jetbrains.mps.lang.structure.structure.ConceptDeclaration" flags="ig" index="1TIwiD">
        <property id="1096454100552" name="rootable" index="19KtqR" />
        <reference id="1071489389519" name="extends" index="1TJDcQ" />
        <child id="1169129564478" name="implements" index="PzmwI" />
      </concept>
      <concept id="1071489288299" name="jetbrains.mps.lang.structure.structure.PropertyDeclaration" flags="ig" index="1TJgyi">
        <property id="241647608299431129" name="propertyId" index="IQ2nx" />
        <reference id="1082985295845" name="dataType" index="AX2Wp" />
      </concept>
      <concept id="1071489288298" name="jetbrains.mps.lang.structure.structure.LinkDeclaration" flags="ig" index="1TJgyj">
        <property id="1071599776563" name="role" index="20kJfa" />
        <property id="1071599893252" name="sourceCardinality" index="20lbJX" />
        <property id="1071599937831" name="metaClass" index="20lmBu" />
        <property id="241647608299431140" name="linkId" index="IQ2ns" />
        <reference id="1071599976176" name="target" index="20lvS9" />
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ng" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
  </registry>
  <node concept="1TIwiD" id="4Yb5JA31wzj">
    <property role="EcuMT" value="5731700211659966675" />
    <property role="TrG5h" value="Library" />
    <property role="19KtqR" value="true" />
    <property role="34LRSv" value="library" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="PrWs8" id="4Yb5JA31wzk" role="PzmwI">
      <ref role="PrY4T" to="tpck:h0TrEE$" resolve="INamedConcept" />
    </node>
    <node concept="1TJgyj" id="4Yb5JA31JNm" role="1TKVEi">
      <property role="IQ2ns" value="5731700211660029142" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20kJfa" value="entities" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" node="4Yb5JA31wzl" resolve="LibraryEntityBase" />
    </node>
  </node>
  <node concept="1TIwiD" id="4Yb5JA31wzl">
    <property role="EcuMT" value="5731700211659966677" />
    <property role="TrG5h" value="LibraryEntityBase" />
    <property role="R5$K7" value="true" />
    <ref role="1TJDcQ" to="tpck:gw2VY9q" resolve="BaseConcept" />
    <node concept="1TJgyi" id="4Yb5JA31wzp" role="1TKVEl">
      <property role="IQ2nx" value="5731700211659966681" />
      <property role="TrG5h" value="isbn" />
      <ref role="AX2Wp" to="tpck:fKAOsGN" resolve="string" />
    </node>
    <node concept="1TJgyi" id="4Yb5JA31wzq" role="1TKVEl">
      <property role="IQ2nx" value="5731700211659966682" />
      <property role="TrG5h" value="available" />
      <ref role="AX2Wp" to="tpck:fKAQMTB" resolve="boolean" />
    </node>
    <node concept="PrWs8" id="4Yb5JA31wzm" role="PzmwI">
      <ref role="PrY4T" to="tpck:h0TrEE$" resolve="INamedConcept" />
    </node>
  </node>
  <node concept="1TIwiD" id="4Yb5JA31wzn">
    <property role="EcuMT" value="5731700211659966679" />
    <property role="TrG5h" value="Book" />
    <ref role="1TJDcQ" node="4Yb5JA31wzl" resolve="LibraryEntityBase" />
    <node concept="1TJgyi" id="4Yb5JA31wzr" role="1TKVEl">
      <property role="IQ2nx" value="5731700211659966683" />
      <property role="TrG5h" value="publicationDate" />
      <ref role="AX2Wp" to="tpck:fKAQMTA" resolve="integer" />
    </node>
    <node concept="1TJgyj" id="4Yb5JA31Nw8" role="1TKVEi">
      <property role="IQ2ns" value="5731700211660044296" />
      <property role="20lmBu" value="fLJjDmT/aggregation" />
      <property role="20kJfa" value="authors" />
      <property role="20lbJX" value="fLJekj5/_0__n" />
      <ref role="20lvS9" to="xcst:4Yb5JA31LCj" resolve="PersonRef" />
    </node>
  </node>
  <node concept="1TIwiD" id="4Yb5JA31wzo">
    <property role="EcuMT" value="5731700211659966680" />
    <property role="TrG5h" value="Magazine" />
    <ref role="1TJDcQ" node="4Yb5JA31wzl" resolve="LibraryEntityBase" />
    <node concept="1TJgyi" id="4Yb5JA31wzx" role="1TKVEl">
      <property role="IQ2nx" value="5731700211659966689" />
      <property role="TrG5h" value="periodicity" />
      <ref role="AX2Wp" node="4Yb5JA31wzs" resolve="EPeriodicity" />
    </node>
  </node>
  <node concept="25R3W" id="4Yb5JA31wzs">
    <property role="3F6X1D" value="5731700211659966684" />
    <property role="TrG5h" value="EPeriodicity" />
    <node concept="25R33" id="4Yb5JA31wzt" role="25R1y">
      <property role="3tVfz5" value="5731700211659966685" />
      <property role="TrG5h" value="WEEKLY" />
    </node>
    <node concept="25R33" id="4Yb5JA31wzu" role="25R1y">
      <property role="3tVfz5" value="5731700211659966686" />
      <property role="TrG5h" value="BI_WEEKLY" />
    </node>
    <node concept="25R33" id="4Yb5JA31wzv" role="25R1y">
      <property role="3tVfz5" value="5731700211659966687" />
      <property role="TrG5h" value="MONTHLY" />
    </node>
    <node concept="25R33" id="4Yb5JA31wzw" role="25R1y">
      <property role="3tVfz5" value="5731700211659966688" />
      <property role="TrG5h" value="QUATERLY" />
    </node>
  </node>
</model>

