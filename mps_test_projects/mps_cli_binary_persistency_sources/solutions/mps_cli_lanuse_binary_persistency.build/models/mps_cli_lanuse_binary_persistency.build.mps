<?xml version="1.0" encoding="UTF-8"?>
<model ref="r:3a5328f9-115e-4727-944e-952353f2ebc4(mps_cli_lanuse_binary_persistency.build)">
  <persistence version="9" />
  <languages>
    <use id="798100da-4f0a-421a-b991-71f8c50ce5d2" name="jetbrains.mps.build" version="0" />
    <use id="0cf935df-4699-4e9c-a132-fa109541cba3" name="jetbrains.mps.build.mps" version="8" />
  </languages>
  <imports>
    <import index="ffeo" ref="r:874d959d-e3b4-4d04-b931-ca849af130dd(jetbrains.mps.ide.build)" />
  </imports>
  <registry>
    <language id="479c7a8c-02f9-43b5-9139-d910cb22f298" name="jetbrains.mps.core.xml">
      <concept id="6666499814681415858" name="jetbrains.mps.core.xml.structure.XmlElement" flags="ng" index="2pNNFK">
        <property id="6666499814681415862" name="tagName" index="2pNNFO" />
        <child id="1622293396948928802" name="content" index="3o6s8t" />
      </concept>
      <concept id="1622293396948952339" name="jetbrains.mps.core.xml.structure.XmlText" flags="nn" index="3o6iSG">
        <property id="1622293396948953704" name="value" index="3o6i5n" />
      </concept>
    </language>
    <language id="798100da-4f0a-421a-b991-71f8c50ce5d2" name="jetbrains.mps.build">
      <concept id="5481553824944787378" name="jetbrains.mps.build.structure.BuildSourceProjectRelativePath" flags="ng" index="55IIr" />
      <concept id="7321017245476976379" name="jetbrains.mps.build.structure.BuildRelativePath" flags="ng" index="iG8Mu">
        <child id="7321017245477039051" name="compositePart" index="iGT6I" />
      </concept>
      <concept id="4993211115183325728" name="jetbrains.mps.build.structure.BuildProjectDependency" flags="ng" index="2sgV4H">
        <reference id="5617550519002745380" name="script" index="1l3spb" />
        <child id="4129895186893471026" name="artifacts" index="2JcizS" />
      </concept>
      <concept id="4380385936562003279" name="jetbrains.mps.build.structure.BuildString" flags="ng" index="NbPM2">
        <child id="4903714810883783243" name="parts" index="3MwsjC" />
      </concept>
      <concept id="8618885170173601777" name="jetbrains.mps.build.structure.BuildCompositePath" flags="nn" index="2Ry0Ak">
        <property id="8618885170173601779" name="head" index="2Ry0Am" />
        <child id="8618885170173601778" name="tail" index="2Ry0An" />
      </concept>
      <concept id="6647099934206700647" name="jetbrains.mps.build.structure.BuildJavaPlugin" flags="ng" index="10PD9b" />
      <concept id="7389400916848136194" name="jetbrains.mps.build.structure.BuildFolderMacro" flags="ng" index="398rNT">
        <child id="7389400916848144618" name="defaultPath" index="398pKh" />
      </concept>
      <concept id="7389400916848153117" name="jetbrains.mps.build.structure.BuildSourceMacroRelativePath" flags="ng" index="398BVA">
        <reference id="7389400916848153130" name="macro" index="398BVh" />
      </concept>
      <concept id="5617550519002745364" name="jetbrains.mps.build.structure.BuildLayout" flags="ng" index="1l3spV" />
      <concept id="5617550519002745363" name="jetbrains.mps.build.structure.BuildProject" flags="ng" index="1l3spW">
        <property id="5204048710541015587" name="internalBaseDirectory" index="2DA0ip" />
        <child id="6647099934206700656" name="plugins" index="10PD9s" />
        <child id="7389400916848080626" name="parts" index="3989C9" />
        <child id="5617550519002745381" name="dependencies" index="1l3spa" />
        <child id="5617550519002745378" name="macros" index="1l3spd" />
        <child id="5617550519002745372" name="layout" index="1l3spN" />
      </concept>
      <concept id="8654221991637384182" name="jetbrains.mps.build.structure.BuildFileIncludesSelector" flags="ng" index="3qWCbU">
        <property id="8654221991637384184" name="pattern" index="3qWCbO" />
      </concept>
      <concept id="4701820937132344003" name="jetbrains.mps.build.structure.BuildLayout_Container" flags="ngI" index="1y1bJS">
        <child id="7389400916848037006" name="children" index="39821P" />
      </concept>
      <concept id="841011766566059607" name="jetbrains.mps.build.structure.BuildStringNotEmpty" flags="ng" index="3_J27D" />
      <concept id="5248329904287794596" name="jetbrains.mps.build.structure.BuildInputFiles" flags="ng" index="3LXTmp">
        <child id="5248329904287794598" name="dir" index="3LXTmr" />
        <child id="5248329904287794679" name="selectors" index="3LXTna" />
      </concept>
      <concept id="4903714810883702019" name="jetbrains.mps.build.structure.BuildTextStringPart" flags="ng" index="3Mxwew">
        <property id="4903714810883755350" name="text" index="3MwjfP" />
      </concept>
    </language>
    <language id="ceab5195-25ea-4f22-9b92-103b95ca8c0c" name="jetbrains.mps.lang.core">
      <concept id="1169194658468" name="jetbrains.mps.lang.core.structure.INamedConcept" flags="ngI" index="TrEIO">
        <property id="1169194664001" name="name" index="TrG5h" />
      </concept>
    </language>
    <language id="0cf935df-4699-4e9c-a132-fa109541cba3" name="jetbrains.mps.build.mps">
      <concept id="6592112598314586625" name="jetbrains.mps.build.mps.structure.BuildMps_IdeaPluginGroup" flags="ng" index="m$f5U">
        <reference id="6592112598314586626" name="group" index="m$f5T" />
      </concept>
      <concept id="6592112598314498932" name="jetbrains.mps.build.mps.structure.BuildMps_IdeaPlugin" flags="ng" index="m$_wf">
        <property id="6592112598314498927" name="id" index="m$_wk" />
        <child id="1359186315025500371" name="xml" index="20twgj" />
        <child id="6592112598314498931" name="version" index="m$_w8" />
        <child id="6592112598314499050" name="content" index="m$_yh" />
        <child id="6592112598314499028" name="dependencies" index="m$_yJ" />
        <child id="6592112598314499021" name="name" index="m$_yQ" />
        <child id="6592112598314855574" name="containerName" index="m_cZH" />
      </concept>
      <concept id="6592112598314498926" name="jetbrains.mps.build.mps.structure.BuildMpsLayout_Plugin" flags="ng" index="m$_wl">
        <reference id="6592112598314801433" name="plugin" index="m_rDy" />
        <child id="3570488090019868128" name="packagingType" index="pUk7w" />
      </concept>
      <concept id="6592112598314499027" name="jetbrains.mps.build.mps.structure.BuildMps_IdeaPluginDependency" flags="ng" index="m$_yC">
        <reference id="6592112598314499066" name="target" index="m$_y1" />
      </concept>
      <concept id="3570488090019868065" name="jetbrains.mps.build.mps.structure.BuildMpsLayout_AutoPluginLayoutType" flags="ng" index="pUk6x" />
      <concept id="1500819558095907805" name="jetbrains.mps.build.mps.structure.BuildMps_Group" flags="ng" index="2G$12M">
        <child id="1500819558095907806" name="modules" index="2G$12L" />
      </concept>
      <concept id="868032131020265945" name="jetbrains.mps.build.mps.structure.BuildMPSPlugin" flags="ng" index="3b7kt6" />
      <concept id="5253498789149381388" name="jetbrains.mps.build.mps.structure.BuildMps_Module" flags="ng" index="3bQrTs">
        <child id="5253498789149547825" name="sources" index="3bR31x" />
        <child id="5253498789149547704" name="dependencies" index="3bR37C" />
      </concept>
      <concept id="5253498789149585690" name="jetbrains.mps.build.mps.structure.BuildMps_ModuleDependencyOnModule" flags="ng" index="3bR9La">
        <reference id="5253498789149547705" name="module" index="3bR37D" />
      </concept>
      <concept id="763829979718664966" name="jetbrains.mps.build.mps.structure.BuildMps_ModuleResources" flags="ng" index="3rtmxn">
        <child id="763829979718664967" name="files" index="3rtmxm" />
      </concept>
      <concept id="4297162197620964123" name="jetbrains.mps.build.mps.structure.BuildMps_GeneratorOptions" flags="ng" index="1wNqPr" />
      <concept id="5507251971038816436" name="jetbrains.mps.build.mps.structure.BuildMps_Generator" flags="ng" index="1yeLz9" />
      <concept id="4278635856200817744" name="jetbrains.mps.build.mps.structure.BuildMps_ModuleModelRoot" flags="ng" index="1BupzO">
        <property id="8137134783396907368" name="convert2binary" index="1Hdu6h" />
        <property id="8137134783396676838" name="extracted" index="1HemKv" />
        <property id="2889113830911481881" name="deployFolderName" index="3ZfqAx" />
        <child id="8137134783396676835" name="location" index="1HemKq" />
      </concept>
      <concept id="3189788309731840247" name="jetbrains.mps.build.mps.structure.BuildMps_Solution" flags="ng" index="1E1JtA" />
      <concept id="3189788309731840248" name="jetbrains.mps.build.mps.structure.BuildMps_Language" flags="ng" index="1E1JtD">
        <child id="9200313594498201639" name="generator" index="1TViLv" />
      </concept>
      <concept id="322010710375871467" name="jetbrains.mps.build.mps.structure.BuildMps_AbstractModule" flags="ng" index="3LEN3z">
        <property id="8369506495128725901" name="compact" index="BnDLt" />
        <property id="322010710375892619" name="uuid" index="3LESm3" />
        <child id="322010710375956261" name="path" index="3LF7KH" />
      </concept>
      <concept id="7259033139236285166" name="jetbrains.mps.build.mps.structure.BuildMps_ExtractedModuleDependency" flags="nn" index="1SiIV0">
        <child id="7259033139236285167" name="dependency" index="1SiIV1" />
      </concept>
    </language>
  </registry>
  <node concept="1l3spW" id="5T1QuSamlCw">
    <property role="TrG5h" value="mps_cli_lanuse_binary_persistency" />
    <property role="2DA0ip" value="./../../build" />
    <node concept="10PD9b" id="5T1QuSamlCx" role="10PD9s" />
    <node concept="3b7kt6" id="5T1QuSamlCy" role="10PD9s" />
    <node concept="398rNT" id="5T1QuSamlCz" role="1l3spd">
      <property role="TrG5h" value="mps_home" />
      <node concept="55IIr" id="3YCdF829LLP" role="398pKh">
        <node concept="2Ry0Ak" id="3YCdF82a9SL" role="iGT6I">
          <property role="2Ry0Am" value=".." />
          <node concept="2Ry0Ak" id="3YCdF82a9SO" role="2Ry0An">
            <property role="2Ry0Am" value=".." />
            <node concept="2Ry0Ak" id="3YCdF82a9SR" role="2Ry0An">
              <property role="2Ry0Am" value=".." />
              <node concept="2Ry0Ak" id="3YCdF82aBQ1" role="2Ry0An">
                <property role="2Ry0Am" value=".." />
                <node concept="2Ry0Ak" id="3YCdF82aBQ2" role="2Ry0An">
                  <property role="2Ry0Am" value="MPS_20241.19416.1372" />
                </node>
              </node>
            </node>
          </node>
        </node>
      </node>
    </node>
    <node concept="398rNT" id="3YCdF829LLR" role="1l3spd">
      <property role="TrG5h" value="landefs" />
      <node concept="55IIr" id="3YCdF829LLU" role="398pKh">
        <node concept="2Ry0Ak" id="3YCdF829LLY" role="iGT6I">
          <property role="2Ry0Am" value=".." />
          <node concept="2Ry0Ak" id="3YCdF82arQK" role="2Ry0An">
            <property role="2Ry0Am" value=".." />
            <node concept="2Ry0Ak" id="3YCdF82arQL" role="2Ry0An">
              <property role="2Ry0Am" value="mps_cli_landefs" />
            </node>
          </node>
        </node>
      </node>
    </node>
    <node concept="398rNT" id="3YCdF82arQN" role="1l3spd">
      <property role="TrG5h" value="code" />
      <node concept="55IIr" id="3YCdF82arQP" role="398pKh">
        <node concept="2Ry0Ak" id="3YCdF82arQR" role="iGT6I">
          <property role="2Ry0Am" value=".." />
        </node>
      </node>
    </node>
    <node concept="2sgV4H" id="5T1QuSamlC$" role="1l3spa">
      <ref role="1l3spb" to="ffeo:3IKDaVZmzS6" resolve="mps" />
      <node concept="398BVA" id="5T1QuSamlC_" role="2JcizS">
        <ref role="398BVh" node="5T1QuSamlCz" resolve="mps_home" />
      </node>
    </node>
    <node concept="1l3spV" id="5T1QuSamlDl" role="1l3spN">
      <node concept="m$_wl" id="3YCdF82afTI" role="39821P">
        <ref role="m_rDy" node="5T1QuSamlD8" resolve="mps_cli_lanuse_binary_persistency" />
        <node concept="pUk6x" id="3YCdF82afTM" role="pUk7w" />
      </node>
    </node>
    <node concept="m$_wf" id="5T1QuSamlD8" role="3989C9">
      <property role="m$_wk" value="mps_cli_lanuse_binary_persistency" />
      <node concept="3_J27D" id="5T1QuSamlD9" role="m$_yQ">
        <node concept="3Mxwew" id="5T1QuSamlDa" role="3MwsjC">
          <property role="3MwjfP" value="mps_cli_lanuse_binary_persistency" />
        </node>
      </node>
      <node concept="3_J27D" id="5T1QuSamlDb" role="m$_w8">
        <node concept="3Mxwew" id="5T1QuSamlDc" role="3MwsjC">
          <property role="3MwjfP" value="1.0" />
        </node>
      </node>
      <node concept="m$f5U" id="5T1QuSamlDd" role="m$_yh">
        <ref role="m$f5T" node="5T1QuSamlD7" resolve="mps_cli_lanuse_binary_persistency" />
      </node>
      <node concept="m$_yC" id="5T1QuSamlDe" role="m$_yJ">
        <ref role="m$_y1" to="ffeo:4k71ibbKLe8" resolve="jetbrains.mps.core" />
      </node>
      <node concept="3_J27D" id="5T1QuSamlDf" role="m_cZH">
        <node concept="3Mxwew" id="5T1QuSamlDg" role="3MwsjC">
          <property role="3MwjfP" value="mps_cli_lanuse_binary_persistency" />
        </node>
      </node>
      <node concept="2pNNFK" id="5T1QuSamlDh" role="20twgj">
        <property role="2pNNFO" value="depends" />
        <node concept="3o6iSG" id="5T1QuSamlDi" role="3o6s8t">
          <property role="3o6i5n" value="com.intellij.modules.platform" />
        </node>
      </node>
    </node>
    <node concept="1wNqPr" id="3YCdF82a3RJ" role="3989C9" />
    <node concept="2G$12M" id="5T1QuSamlD7" role="3989C9">
      <property role="TrG5h" value="mps_cli_lanuse_binary_persistency" />
      <node concept="1E1JtD" id="5T1QuSamlE3" role="2G$12L">
        <property role="BnDLt" value="true" />
        <property role="TrG5h" value="mps.cli.landefs.library" />
        <property role="3LESm3" value="53fdadc6-a07c-4398-b66b-c9af1071186c" />
        <node concept="398BVA" id="3YCdF829LMe" role="3LF7KH">
          <ref role="398BVh" node="3YCdF829LLR" resolve="landefs" />
          <node concept="2Ry0Ak" id="3YCdF829LMn" role="iGT6I">
            <property role="2Ry0Am" value="languages" />
            <node concept="2Ry0Ak" id="3YCdF829LMo" role="2Ry0An">
              <property role="2Ry0Am" value="mps.cli.landefs.library" />
              <node concept="2Ry0Ak" id="3YCdF829LMq" role="2Ry0An">
                <property role="2Ry0Am" value="mps.cli.landefs.library.mpl" />
              </node>
            </node>
          </node>
        </node>
        <node concept="1BupzO" id="3YCdF829LMv" role="3bR31x">
          <property role="3ZfqAx" value="models" />
          <property role="1Hdu6h" value="true" />
          <property role="1HemKv" value="true" />
          <node concept="3LXTmp" id="3YCdF829LMw" role="1HemKq">
            <node concept="398BVA" id="3YCdF829LMr" role="3LXTmr">
              <ref role="398BVh" node="3YCdF829LLR" resolve="landefs" />
              <node concept="2Ry0Ak" id="3YCdF829LMs" role="iGT6I">
                <property role="2Ry0Am" value="languages" />
                <node concept="2Ry0Ak" id="3YCdF829LMt" role="2Ry0An">
                  <property role="2Ry0Am" value="mps.cli.landefs.library" />
                  <node concept="2Ry0Ak" id="3YCdF829LMu" role="2Ry0An">
                    <property role="2Ry0Am" value="models" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="3qWCbU" id="3YCdF829LMx" role="3LXTna">
              <property role="3qWCbO" value="**/*.mps, **/*.mpsr, **/.model" />
            </node>
          </node>
        </node>
        <node concept="1yeLz9" id="3YCdF829LMy" role="1TViLv">
          <property role="TrG5h" value="mps.cli.landefs.library.generator" />
          <property role="3LESm3" value="f4351676-1c67-466c-82ef-b6a08575dc3a" />
          <node concept="1BupzO" id="3YCdF829LMC" role="3bR31x">
            <property role="3ZfqAx" value="generator/templates" />
            <property role="1Hdu6h" value="true" />
            <property role="1HemKv" value="true" />
            <node concept="3LXTmp" id="3YCdF829LMD" role="1HemKq">
              <node concept="398BVA" id="3YCdF829LMz" role="3LXTmr">
                <ref role="398BVh" node="3YCdF829LLR" resolve="landefs" />
                <node concept="2Ry0Ak" id="3YCdF829LM$" role="iGT6I">
                  <property role="2Ry0Am" value="languages" />
                  <node concept="2Ry0Ak" id="3YCdF829LM_" role="2Ry0An">
                    <property role="2Ry0Am" value="mps.cli.landefs.library" />
                    <node concept="2Ry0Ak" id="3YCdF829LMA" role="2Ry0An">
                      <property role="2Ry0Am" value="generator" />
                      <node concept="2Ry0Ak" id="3YCdF829LMB" role="2Ry0An">
                        <property role="2Ry0Am" value="templates" />
                      </node>
                    </node>
                  </node>
                </node>
              </node>
              <node concept="3qWCbU" id="3YCdF829LME" role="3LXTna">
                <property role="3qWCbO" value="**/*.mps, **/*.mpsr, **/.model" />
              </node>
            </node>
          </node>
        </node>
        <node concept="1SiIV0" id="3YCdF829LNT" role="3bR37C">
          <node concept="3bR9La" id="3YCdF829LNU" role="1SiIV1">
            <ref role="3bR37D" node="3YCdF829LN1" resolve="mps.cli.landefs.people" />
          </node>
        </node>
        <node concept="3rtmxn" id="3YCdF829LOt" role="3bR31x">
          <node concept="3LXTmp" id="3YCdF829LOu" role="3rtmxm">
            <node concept="398BVA" id="3YCdF829LOv" role="3LXTmr">
              <ref role="398BVh" node="3YCdF829LLR" resolve="landefs" />
              <node concept="2Ry0Ak" id="3YCdF829LOw" role="iGT6I">
                <property role="2Ry0Am" value="languages" />
                <node concept="2Ry0Ak" id="3YCdF829LOx" role="2Ry0An">
                  <property role="2Ry0Am" value="mps.cli.landefs.library" />
                </node>
              </node>
            </node>
            <node concept="3qWCbU" id="3YCdF829LOz" role="3LXTna">
              <property role="3qWCbO" value="icons/**, resources/**" />
            </node>
          </node>
        </node>
      </node>
      <node concept="1E1JtD" id="3YCdF829LN1" role="2G$12L">
        <property role="BnDLt" value="true" />
        <property role="TrG5h" value="mps.cli.landefs.people" />
        <property role="3LESm3" value="a7aaae55-aa5e-4a05-b2d0-013745658efa" />
        <node concept="398BVA" id="3YCdF829LN5" role="3LF7KH">
          <ref role="398BVh" node="3YCdF829LLR" resolve="landefs" />
          <node concept="2Ry0Ak" id="3YCdF829LN9" role="iGT6I">
            <property role="2Ry0Am" value="languages" />
            <node concept="2Ry0Ak" id="3YCdF829LNc" role="2Ry0An">
              <property role="2Ry0Am" value="mps.cli.landefs.people" />
              <node concept="2Ry0Ak" id="3YCdF829LNf" role="2Ry0An">
                <property role="2Ry0Am" value="mps.cli.landefs.people.mpl" />
              </node>
            </node>
          </node>
        </node>
        <node concept="1BupzO" id="3YCdF829LNt" role="3bR31x">
          <property role="3ZfqAx" value="models" />
          <property role="1Hdu6h" value="true" />
          <property role="1HemKv" value="true" />
          <node concept="3LXTmp" id="3YCdF829LNu" role="1HemKq">
            <node concept="398BVA" id="3YCdF829LNp" role="3LXTmr">
              <ref role="398BVh" node="3YCdF829LLR" resolve="landefs" />
              <node concept="2Ry0Ak" id="3YCdF829LNq" role="iGT6I">
                <property role="2Ry0Am" value="languages" />
                <node concept="2Ry0Ak" id="3YCdF829LNr" role="2Ry0An">
                  <property role="2Ry0Am" value="mps.cli.landefs.people" />
                  <node concept="2Ry0Ak" id="3YCdF829LNs" role="2Ry0An">
                    <property role="2Ry0Am" value="models" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="3qWCbU" id="3YCdF829LNv" role="3LXTna">
              <property role="3qWCbO" value="**/*.mps, **/*.mpsr, **/.model" />
            </node>
          </node>
        </node>
        <node concept="1yeLz9" id="3YCdF829LNw" role="1TViLv">
          <property role="TrG5h" value="mps.cli.landefs.people.generator" />
          <property role="3LESm3" value="9676f44e-4330-48f5-9415-c9740706d681" />
          <node concept="1BupzO" id="3YCdF829LNA" role="3bR31x">
            <property role="3ZfqAx" value="generator/templates" />
            <property role="1Hdu6h" value="true" />
            <property role="1HemKv" value="true" />
            <node concept="3LXTmp" id="3YCdF829LNB" role="1HemKq">
              <node concept="398BVA" id="3YCdF829LNx" role="3LXTmr">
                <ref role="398BVh" node="3YCdF829LLR" resolve="landefs" />
                <node concept="2Ry0Ak" id="3YCdF829LNy" role="iGT6I">
                  <property role="2Ry0Am" value="languages" />
                  <node concept="2Ry0Ak" id="3YCdF829LNz" role="2Ry0An">
                    <property role="2Ry0Am" value="mps.cli.landefs.people" />
                    <node concept="2Ry0Ak" id="3YCdF829LN$" role="2Ry0An">
                      <property role="2Ry0Am" value="generator" />
                      <node concept="2Ry0Ak" id="3YCdF829LN_" role="2Ry0An">
                        <property role="2Ry0Am" value="templates" />
                      </node>
                    </node>
                  </node>
                </node>
              </node>
              <node concept="3qWCbU" id="3YCdF829LNC" role="3LXTna">
                <property role="3qWCbO" value="**/*.mps, **/*.mpsr, **/.model" />
              </node>
            </node>
          </node>
        </node>
        <node concept="3rtmxn" id="3YCdF829LO$" role="3bR31x">
          <node concept="3LXTmp" id="3YCdF829LO_" role="3rtmxm">
            <node concept="398BVA" id="3YCdF829LOA" role="3LXTmr">
              <ref role="398BVh" node="3YCdF829LLR" resolve="landefs" />
              <node concept="2Ry0Ak" id="3YCdF829LOB" role="iGT6I">
                <property role="2Ry0Am" value="languages" />
                <node concept="2Ry0Ak" id="3YCdF829LOC" role="2Ry0An">
                  <property role="2Ry0Am" value="mps.cli.landefs.people" />
                </node>
              </node>
            </node>
            <node concept="3qWCbU" id="3YCdF829LOE" role="3LXTna">
              <property role="3qWCbO" value="icons/**, resources/**" />
            </node>
          </node>
        </node>
      </node>
      <node concept="1E1JtA" id="5T1QuSamlD0" role="2G$12L">
        <property role="BnDLt" value="true" />
        <property role="TrG5h" value="mps.cli.lanuse.library_top.binary_persistency" />
        <property role="3LESm3" value="7c712852-79e9-4a66-9752-404fe92e52e3" />
        <node concept="398BVA" id="3YCdF82arQW" role="3LF7KH">
          <ref role="398BVh" node="3YCdF82arQN" resolve="code" />
          <node concept="2Ry0Ak" id="3YCdF82arR1" role="iGT6I">
            <property role="2Ry0Am" value="solutions" />
            <node concept="2Ry0Ak" id="3YCdF82arR2" role="2Ry0An">
              <property role="2Ry0Am" value="mps.cli.lanuse.library_top.binary_persistency" />
              <node concept="2Ry0Ak" id="3YCdF82arR3" role="2Ry0An">
                <property role="2Ry0Am" value="mps.cli.lanuse.library_top.binary_persistency.msd" />
              </node>
            </node>
          </node>
        </node>
        <node concept="1BupzO" id="5T1QuSamlDv" role="3bR31x">
          <property role="3ZfqAx" value="models" />
          <property role="1Hdu6h" value="true" />
          <property role="1HemKv" value="true" />
          <node concept="3LXTmp" id="3YCdF829LMN" role="1HemKq">
            <node concept="398BVA" id="3YCdF829LMF" role="3LXTmr">
              <ref role="398BVh" node="5T1QuSamlCz" resolve="mps_home" />
              <node concept="2Ry0Ak" id="3YCdF829LMG" role="iGT6I">
                <property role="2Ry0Am" value="solutions" />
                <node concept="2Ry0Ak" id="3YCdF829LMH" role="2Ry0An">
                  <property role="2Ry0Am" value="mps.cli.lanuse.library_top.binary_persistency" />
                  <node concept="2Ry0Ak" id="3YCdF829LMI" role="2Ry0An">
                    <property role="2Ry0Am" value="models" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="3qWCbU" id="3YCdF829LMO" role="3LXTna">
              <property role="3qWCbO" value="**/*.mps, **/*.mpsr, **/.model" />
            </node>
          </node>
        </node>
      </node>
      <node concept="1E1JtA" id="5T1QuSamlD6" role="2G$12L">
        <property role="BnDLt" value="true" />
        <property role="TrG5h" value="mps.cli.lanuse.library_second.binary_persistency" />
        <property role="3LESm3" value="14c68ffa-2028-4f5b-92c7-52adc82fcb47" />
        <node concept="398BVA" id="3YCdF82arR8" role="3LF7KH">
          <ref role="398BVh" node="3YCdF82arQN" resolve="code" />
          <node concept="2Ry0Ak" id="3YCdF82arRd" role="iGT6I">
            <property role="2Ry0Am" value="solutions" />
            <node concept="2Ry0Ak" id="3YCdF82arRe" role="2Ry0An">
              <property role="2Ry0Am" value="mps.cli.lanuse.library_second.binary_persistency" />
              <node concept="2Ry0Ak" id="3YCdF82arRf" role="2Ry0An">
                <property role="2Ry0Am" value="mps.cli.lanuse.library_second.binary_persistency.msd" />
              </node>
            </node>
          </node>
        </node>
        <node concept="1BupzO" id="5T1QuSamlDA" role="3bR31x">
          <property role="3ZfqAx" value="models" />
          <property role="1Hdu6h" value="true" />
          <property role="1HemKv" value="true" />
          <node concept="3LXTmp" id="3YCdF829LMX" role="1HemKq">
            <node concept="398BVA" id="3YCdF829LMP" role="3LXTmr">
              <ref role="398BVh" node="5T1QuSamlCz" resolve="mps_home" />
              <node concept="2Ry0Ak" id="3YCdF829LMQ" role="iGT6I">
                <property role="2Ry0Am" value="solutions" />
                <node concept="2Ry0Ak" id="3YCdF829LMR" role="2Ry0An">
                  <property role="2Ry0Am" value="mps.cli.lanuse.library_second.binary_persistency" />
                  <node concept="2Ry0Ak" id="3YCdF829LMS" role="2Ry0An">
                    <property role="2Ry0Am" value="models" />
                  </node>
                </node>
              </node>
            </node>
            <node concept="3qWCbU" id="3YCdF829LMY" role="3LXTna">
              <property role="3qWCbO" value="**/*.mps, **/*.mpsr, **/.model" />
            </node>
          </node>
        </node>
        <node concept="1SiIV0" id="5T1QuSamlDJ" role="3bR37C">
          <node concept="3bR9La" id="5T1QuSamlDK" role="1SiIV1">
            <ref role="3bR37D" node="5T1QuSamlD0" resolve="mps.cli.lanuse.library_top.binary_persistency" />
          </node>
        </node>
      </node>
    </node>
  </node>
</model>

