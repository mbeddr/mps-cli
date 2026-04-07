from mpscli.model.builder.binary.model_input_stream import ModelInputStream
from mpscli.model.builder.binary.registry import load_registry
from mpscli.model.builder.binary.nodes import read_children
from mpscli.model.builder.SModelBuilderBase import SModelBuilderBase
from mpscli.model.SModel import SModel

_V2 = ModelInputStream.STREAM_ID_V2
_V3 = ModelInputStream.STREAM_ID_V3


class _UnknownSubKind(RuntimeError):
    def __init__(self, sub_hex: str, pos: int):
        super().__init__(f"Unsupported model ref sub-kind {sub_hex} at pos {pos}")
        self.sub_hex = sub_hex
        self.pos = pos


class SModelBuilderBinaryPersistency(SModelBuilderBase):
    """
    Full binary parser for JetBrains MPS .mpb files.

    High-level parse order:
        1. Header  (HEADER_START to HEADER_END)
        2. Registry (REGISTRY_START to REGISTRY_END)
        3. Model properties  — structure differs for V2 vs V3:
               V2:
                   loadUsedLanguagesV2  (u16 count, each is uuid + string)
                   loadModuleRefList    (engaged languages)
                   loadModuleRefList    (devkits)
                   loadImports V2  (u32 count, each is model_ref + i32 version)
               V3:
                   readByte DEPENDENCY_V1 (0x01)
                   loadUsedLanguagesV3 (u16 count, each is readLanguage + i32 version)
                   loadEngagedLanguages   (u16 count, each is readLanguage)
                   loadModuleRefList      (devkits)
                   loadImports V3  (u32 count, each is model_ref)
        4. MODEL_START marker
        5. Node tree
    """

    # TODO - check if V2 format support is really needed or already obsolete

    def __init__(self):
        super().__init__()

        self.index_2_concept = {}
        self.index_2_property = {}
        self.index_2_reference_role = {}
        self.index_2_child_role_in_parent = {}
        self.concept_id_2_concept = {}
        self.index_2_imported_model_uuid = {}

        self.stream_version = None

    def _uuid_str(self, high: int, low: int) -> str:
        # format two u64 values as a Java-style uuid string with dashes.
        return (
            f"r:{high >> 32:08x}-{(high >> 16) & 0xffff:04x}-"
            f"{high & 0xffff:04x}-{(low >> 48) & 0xffff:04x}-"
            f"{low & 0xffffffffffff:012x}"
        )

    def build(self, path_to_model: str):
        with open(path_to_model, "rb") as f:
            data = f.read()

        reader = ModelInputStream(data)

        # 1. header
        version, model_uuid, model_name = self._load_header(reader)
        self.stream_version = version

        # create the model with real uuid+name from header
        uuid_str = model_uuid or "r:unknown"
        name_str = model_name or "unknown.model"
        model = SModel(name_str, uuid_str, False)
        self.index_2_imported_model_uuid["0"] = uuid_str

        # 2. registry
        load_registry(reader, self)

        # 3. model properties
        try:
            self._load_model_properties(reader, version)
        except _UnknownSubKind as e:
            import warnings

            warnings.warn(f"[build] {path_to_model}: {e} — skipped to MODEL_START")
            self._skip_to_marker(reader, ModelInputStream.MODEL_START)
            return model

        # 4. model start
        token = reader.read_u32()
        if token != ModelInputStream.MODEL_START:
            raise RuntimeError(
                f"Expected MODEL_START (0x{ModelInputStream.MODEL_START:08X}), "
                f"got 0x{token:08X} at pos {reader.tell() - 4}"
            )

        # 5. node tree
        read_children(reader, self, model, None)

        return model

    def _load_header(self, reader: ModelInputStream) -> int:
        if reader.read_u32() != ModelInputStream.HEADER_START:
            raise RuntimeError("Expected HEADER_START")

        version = reader.read_u32()
        if version == ModelInputStream.STREAM_ID_V1:
            raise RuntimeError("V1 binary format not supported — please re-save models")
        if version not in (_V2, _V3):
            raise RuntimeError(f"Unknown stream version: 0x{version:08X}")

        if version == _V2:
            # readModelReference()
            _model_uuid, _model_name = self._read_model_reference_v2(reader)
            # model version field
            reader.read_i32()
            # check for optional HEADER_ATTRIBUTES block
            sync = reader.read_u8()
            if sync == ModelInputStream.HEADER_ATTRIBUTES:
                # placeholder boolean (V2)
                reader.read_bool()
                props_count = reader.read_i16()
            else:
                # no attributes block so put the byte back logically by adjusting pos
                reader.seek(reader.tell() - 1)
                props_count = 0
        else:
            # v3
            # module reference (may be null)
            reader.read_module_ref()
            # model id
            _model_uuid = self._read_model_id(reader)
            # model name
            _model_name = reader.read_string()
            sync = reader.read_u8()
            if sync != ModelInputStream.HEADER_ATTRIBUTES:
                raise RuntimeError(
                    f"Expected HEADER_ATTRIBUTES (0x{ModelInputStream.HEADER_ATTRIBUTES:02X}), "
                    f"got 0x{sync:02X} at pos {reader.tell() - 1}"
                )
            props_count = reader.read_i16()

        # optional model properties (key/value pairs)
        for _ in range(props_count):
            # key — adds to string table
            reader.read_string()
            # value - adds to string table
            reader.read_string()

        if version == _V3:
            reader.read_u8()  # persistedCapabilities byte

        # HEADER_END marker
        if reader.read_u32() != ModelInputStream.HEADER_END:
            raise RuntimeError("Expected HEADER_END")

        return version, _model_uuid, _model_name

    def _read_model_reference_v2(self, reader: ModelInputStream):
        kind = reader.read_u8()
        # NULL model reference
        if kind == 0x70:
            return None, None
        reader.read_u8()
        # regular model id is uuid (2×u64)
        high, low = reader.read_uuid()
        uuid_str = self._uuid_str(high, low)
        # model long name is added to string table
        name = reader.read_string()
        # declaring module ref
        reader.read_module_ref()
        return uuid_str, name

    def _read_model_id(self, reader: ModelInputStream):
        kind = reader.read_u8()
        # NULL
        if kind == 0x70:
            return None
        # uuid-based
        if kind == 0x48:
            high, low = reader.read_uuid()
            return self._uuid_str(high, low)
        # string-based
        elif kind == 0x47:
            return reader.read_string()
        # unknown kind
        return None

    def _load_model_properties(self, reader: ModelInputStream, version: int):
        if version == _V2:
            self._load_used_languages_v2(reader)
            # engaged languages
            self._load_module_ref_list(reader)
            # devkits
            self._load_module_ref_list(reader)
            self._load_imports(reader, version)
        else:
            dep_fmt = reader.read_u8()
            if dep_fmt != ModelInputStream.DEPENDENCY_V1:
                raise RuntimeError(
                    f"Unknown dependency format: 0x{dep_fmt:02X} at pos {reader.tell() - 1}"
                )
            self._load_used_languages_v3(reader)
            self._load_engaged_languages(reader)
            # devkits
            self._load_module_ref_list(reader)
            self._load_imports(reader, version)

    def _load_used_languages_v2(self, reader: ModelInputStream):
        count = reader.read_u16()
        for _ in range(count):
            # language uuid
            reader.read_uuid()
            # language name
            reader.read_string()

    def _load_used_languages_v3(self, reader: ModelInputStream):
        """
        V3: u16 count and each entry is readLanguage() + i32 import version.
        readLanguage() = uuid + string name (same as V2 per-entry).
        """
        count = reader.read_u16()
        for _ in range(count):
            # language uuid
            reader.read_uuid()
            # language name
            reader.read_string()
            # import version
            reader.read_i32()

    def _load_engaged_languages(self, reader: ModelInputStream):
        count = reader.read_u16()
        for _ in range(count):
            reader.read_uuid()
            reader.read_string()

    def _load_module_ref_list(self, reader: ModelInputStream):
        count = reader.read_u16()
        for _ in range(count):
            reader.read_module_ref()

    def _load_imports(self, reader: ModelInputStream, version: int):
        count = reader.read_u32()
        for i in range(count):
            model_id = self._read_model_reference(reader)
            if version == _V2:
                # import element version (V2 only)
                reader.read_i32()
            self.index_2_imported_model_uuid[str(i + 1)] = model_id or ""

    def _read_model_reference(self, reader: ModelInputStream):
        kind = reader.read_u8()
        # NULL model reference
        if kind == 0x70:
            return None

        sub = reader.read_u8()
        # regular: uuid-based SModelId
        if sub == 0x28:
            uuid = reader.read_uuid()
            model_id = self._uuid_str(uuid[0], uuid[1])
            # model long name
            reader.read_string()
            reader.read_module_ref()

        # foreign: string-based SModelId (java stubs)
        elif sub == 0x26:
            # example - "java:java.lang"
            model_id = reader.read_string()
            # model name example "java.lang@java_stub"
            reader.read_string()
            # declaring module reference
            reader.read_module_ref()

        else:
            raise _UnknownSubKind(f"0x{sub:02X}", reader.tell())

        return model_id

    def _skip_to_marker(self, reader: ModelInputStream, marker: int):
        target = marker.to_bytes(4, "big")
        start = reader.pos
        while reader.pos + 4 <= len(reader.data):
            if reader.data[reader.pos : reader.pos + 4] == target:
                reader.pos += 4
                return
            reader.pos += 1
        raise RuntimeError(f"Marker 0x{marker:08X} not found from pos {start}")
