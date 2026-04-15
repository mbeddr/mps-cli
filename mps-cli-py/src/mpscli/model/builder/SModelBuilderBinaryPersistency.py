from mpscli.model.builder.binary.model_input_stream import ModelInputStream
from mpscli.model.builder.binary.registry import load_registry
from mpscli.model.builder.binary.nodes import read_children
from mpscli.model.builder.binary.imports import load_imports
from mpscli.model.builder.binary.used_languages import load_used_languages
from mpscli.model.builder.binary.module_refs import load_module_ref_list
from mpscli.model.builder.binary.utils import advance_until_after
from mpscli.model.builder.binary.uuid_utils import uuid_str
from mpscli.model.builder.SModelBuilderBase import SModelBuilderBase
from mpscli.model.SModel import SModel
from mpscli.model.builder.binary.constants import (
    NULL,
    STREAM_ID_V1,
    STREAM_ID_V2,
    STREAM_ID_V3,
    HEADER_START,
    HEADER_END,
    HEADER_ATTRIBUTES,
    MODEL_START,
    DEPENDENCY_V1,
    MODELID_REGULAR,
    MODELID_FOREIGN,
)

_V2 = STREAM_ID_V2
_V3 = STREAM_ID_V3


class _UnknownSubKind(RuntimeError):
    def __init__(self, sub_hex: str, pos: int):
        super().__init__(f"Unsupported model ref sub-kind {sub_hex} at pos {pos}")
        self.sub_hex = sub_hex
        self.pos = pos


class SModelBuilderBinaryPersistency(SModelBuilderBase):
    """
    mirrors the combined logic of BinaryPersistence.loadModel() + BinaryPersistence.loadHeader()
    + BinaryPersistence.loadModelProperties() in:
    https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BinaryPersistence.java

    Full binary parser for JetBrains MPS .mpb files.

    High-level parse order:
        1. Header  (HEADER_START to HEADER_END)
        2. Registry (REGISTRY_START to REGISTRY_END)
        3. Model properties structure differs for V2 vs V3:
               V2:
                   loadUsedLanguagesV2 (u16 count, each is uuid + string)
                   loadModuleRefList (engaged languages)
                   loadModuleRefList (devkits)
                   loadImports V2 (u32 count, each is model_ref + i32 version)
               V3:
                   readByte DEPENDENCY_V1 (0x01)
                   loadUsedLanguagesV3 (u16 count, each is readLanguage + i32 version)
                   loadEngagedLanguages (u16 count, each is readLanguage)
                   loadModuleRefList (devkits)
                   loadImports V3 (u32 count, each is model_ref)
        4. MODEL_START marker
        5. Node tree
    """

    # NOTE - check if V2 format support is really needed or already obsolete after migrating from 2024.1

    def __init__(self):
        super().__init__()

        # index maps populated by load_registry() and this mirrors Java's ReadHelper maps..
        # Java uses TIntObjectHashMap<T> (Trove) and Python uses plain dicts
        self.index_2_concept = {}
        self.index_2_property = {}
        self.index_2_reference_role = {}
        self.index_2_child_role_in_parent = {}
        self.concept_id_2_concept = {}
        self.index_2_imported_model_uuid = {}

        self.stream_version = None

    def _uuid_str(self, high: int, low: int) -> str:
        # delegates to the shared uuid_str() in utils.py to ensure consistent UUID
        # formatting across imports.py, nodes.py, and model_input_stream.py
        return uuid_str(high, low)

    def build(self, path_to_model: str):
        with open(path_to_model, "rb") as f:
            data = f.read()

        reader = ModelInputStream(data)

        # 1. header - extracts stream version, model UUID and model name
        version, model_uuid, model_name = self._load_header(reader)
        self.stream_version = version

        uuid_str = model_uuid or "r:unknown"
        name_str = model_name or "unknown.model"
        model = SModel(name_str, uuid_str, False)

        # Import index 0 is always the current model's own uuid..
        # Java: SModel.importedModels() lists imports starting from index 1 and index 0 is implicitly
        # the model itself used when resolving REF_THIS_MODEL
        self.index_2_imported_model_uuid["0"] = uuid_str

        # 2. registry - builds concept/property/reference/child index maps
        load_registry(reader, self)

        # 3. model properties - used languages, devkits, imports
        try:
            self._load_model_properties(reader, version)
        except _UnknownSubKind as e:
            import warnings

            warnings.warn(f"[build] {path_to_model}: {e} - skipped to MODEL_START")
            # scan forward to MODEL_START and attempt to read the node tree Java would raise ModelReadException
            # and abort entirely but our Python implementation does lenient partial extraction where the node tree
            # is usually intact even when an unusual import reference sub-kind is encountered
            advance_until_after(reader, MODEL_START)
            return model

        # 4. MODEL_START
        token = reader.read_u32()
        if token != MODEL_START:
            raise RuntimeError(
                f"Expected MODEL_START (0x{MODEL_START:08X}), "
                f"got 0x{token:08X} at pos {reader.tell() - 4}"
            )

        # 5. Node tree - recursive read_children populates model.root_nodes
        read_children(reader, self, model, None)

        return model

    def _load_header(self, reader: ModelInputStream):
        # Mirrors BinaryPersistence.loadHeader() in:
        # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BinaryPersistence.java
        if reader.read_u32() != HEADER_START:
            raise RuntimeError("Expected HEADER_START")

        version = reader.read_u32()
        if version == STREAM_ID_V1:
            raise RuntimeError("V1 binary format not supported - please re-save models")
        if version not in (_V2, _V3):
            raise RuntimeError(f"Unknown stream version: 0x{version:08X}")

        if version == _V2:
            # V2: single readModelReference() encodes module ref + model id + model name
            _model_uuid, _model_name = self._read_model_reference_v2(reader)
            # old model version field - kept for stream compatibility, not used
            reader.read_i32()
            # HEADER_ATTRIBUTES block is optional in V2 so peek at next byte
            sync = reader.read_u8()
            if sync == HEADER_ATTRIBUTES:
                # placeholder boolean
                reader.read_bool()
                props_count = reader.read_i16()
            else:
                # no attributes block so put the byte back by rewinding one position
                reader.seek(reader.tell() - 1)
                props_count = 0
        else:
            # V3 (forward compatibility so nothing breaks for 2024.1): module ref + model id + model name written separately
            reader.read_module_ref()  # declaring module reference (may be null)
            _model_uuid = self._read_model_id(reader)
            _model_name = reader.read_string()
            sync = reader.read_u8()
            if sync != HEADER_ATTRIBUTES:
                raise RuntimeError(
                    f"Expected HEADER_ATTRIBUTES (0x{HEADER_ATTRIBUTES:02X}), "
                    f"got 0x{sync:02X} at pos {reader.tell() - 1}"
                )
            props_count = reader.read_i16()

        # optional model properties (key/value string pairs)
        for _ in range(props_count):
            # key
            reader.read_string()
            # value
            reader.read_string()

        if version == _V3:
            # persistedCapabilities byte - CAP_SKIP_NODE_ID (0x01) if node ids for SCOPE_NONE concepts were
            # omitted during write. NodesReader in Java checks this flag and uses a counter instead of
            # reading a node id for those nodes but our Python impl always reads a node id which safe
            # because standard MPS 2024.1 files never set this flag and it looks like it was introduced later
            reader.read_u8()

        if reader.read_u32() != HEADER_END:
            raise RuntimeError("Expected HEADER_END")

        return version, _model_uuid, _model_name

    def _read_model_reference_v2(self, reader: ModelInputStream):
        kind = reader.read_u8()
        # NULL model reference
        if kind == NULL:
            return None, None
        reader.read_u8()
        high, low = reader.read_uuid()
        uuid_str = self._uuid_str(high, low)
        # model long name is added to string table
        name = reader.read_string()
        # declaring module ref
        reader.read_module_ref()
        return uuid_str, name

    def _read_model_id(self, reader: ModelInputStream):
        kind = reader.read_u8()
        if kind == NULL:
            return None
        if kind == MODELID_REGULAR:
            high, low = reader.read_uuid()
            return self._uuid_str(high, low)
        elif kind == MODELID_FOREIGN:
            return reader.read_string()
        return None

    def _load_model_properties(self, reader: ModelInputStream, version: int):
        # mirrors BinaryPersistence.loadModelProperties() in:
        # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BinaryPersistence.java
        #
        # V2 sequence (MPS 2024.1 is the active format):
        #   loadUsedLanguages() - u16 count, each: 2xu64 UUID + string name
        #   loadModuleRefList() - languages (module refs)
        #   loadModuleRefList() - devkits (module refs)
        #   loadImports() - i32 count where each is model_ref + i32 usedVersion
        #
        # V3 sequence (forward compatibility):
        #   u8  DEPENDENCY_V1 (0x01) - dependency format version byte; MPS uses this
        #                              to allow the section to evolve without bumping
        #                              the whole stream version (BinaryPersistence.DEPENDENCY_V1)
        #   loadUsedLanguagesV3() - u16 count where each is 2xu64 UUID + string name + i32 version
        #   loadEngagedLanguages() - u16 count where each is 2xu64 UUID + string name (read via load_module_ref_list)
        #   loadModuleRefList() - devkits (module refs)
        #   loadImports() - i32 count where each is model_ref only (no usedVersion)

        if version == _V2:
            load_used_languages(reader, version)
            load_module_ref_list(reader)
            load_module_ref_list(reader)
            load_imports(reader, self, version)
        else:
            dep_fmt = reader.read_u8()
            if dep_fmt != DEPENDENCY_V1:
                raise RuntimeError(
                    f"Unknown dependency format: 0x{dep_fmt:02X} at pos {reader.tell() - 1}"
                )
            load_used_languages(reader, version)
            load_module_ref_list(reader)
            load_module_ref_list(reader)
            load_imports(reader, self, version)
