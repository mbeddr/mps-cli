from mpscli.model.builder.binary.model_input_stream import ModelInputStream
from mpscli.model.builder.binary.registry import load_registry
from mpscli.model.builder.binary.nodes import read_children
from mpscli.model.builder.SModelBuilderBase import SModelBuilderBase
from mpscli.model.SModel import SModel

# ── Stream version aliases ───────────────────────────────────────────────────
_V2 = ModelInputStream.STREAM_ID_V2  # 0x00000400
_V3 = ModelInputStream.STREAM_ID_V3  # 0x00000500


class SModelBuilderBinaryPersistency(SModelBuilderBase):
    """
    Full binary parser for JetBrains MPS .mpb files.

    Follows BinaryPersistence.java loadModel() / loadModelProperties() EXACTLY.

    High-level parse order:
        1. Header  (HEADER_START … HEADER_END)
        2. Registry (REGISTRY_START … REGISTRY_END)
        3. Model properties  — structure differs for V2 vs V3:
               V2:
                   loadUsedLanguagesV2  (u16 count, each: uuid + string)
                   loadModuleRefList    (engaged languages)
                   loadModuleRefList    (devkits)
                   loadImports V2      (u32 count, each: model_ref + i32 version)
               V3:
                   readByte DEPENDENCY_V1 (0x01)
                   loadUsedLanguagesV3  (u16 count, each: readLanguage + i32 version)
                   loadEngagedLanguages (u16 count, each: readLanguage)
                   loadModuleRefList    (devkits)
                   loadImports V3      (u32 count, each: model_ref, no extra int)
        4. MODEL_START marker
        5. Node tree
    """

    def __init__(self):
        super().__init__()

        self.index_2_concept = {}
        self.index_2_property = {}
        self.index_2_reference_role = {}
        self.index_2_child_role_in_parent = {}
        self.concept_id_2_concept = {}
        self.index_2_imported_model_uuid = {}

        self.stream_version = None

    # ────────────────────────────────────────────────────────────────────────

    def build(self, path_to_model: str):
        print(f"\n[build] Parsing MPB: {path_to_model}")

        with open(path_to_model, "rb") as f:
            data = f.read()

        reader = ModelInputStream(data)
        self._dump_markers(reader)

        # ── 1. Header ──────────────────────────────────────────────────────
        version = self._load_header(reader)
        self.stream_version = version
        print(f"[build] Header OK  version=0x{version:08X}  pos={reader.tell()}")

        # Bootstrap model placeholder so import index 0 resolves
        model = SModel("unknown.model", "r:unknown", False)
        self.index_2_imported_model_uuid["0"] = model.uuid

        # ── 2. Registry ────────────────────────────────────────────────────
        load_registry(reader, self)
        print(f"[build] Registry OK  pos={reader.tell()}")

        # ── 3. Model properties ────────────────────────────────────────────
        self._load_model_properties(reader, version)
        print(f"[build] Model properties OK  pos={reader.tell()}")

        # ── 4. MODEL_START ─────────────────────────────────────────────────
        token = reader.read_u32()
        if token != ModelInputStream.MODEL_START:
            raise RuntimeError(
                f"Expected MODEL_START (0x{ModelInputStream.MODEL_START:08X}), "
                f"got 0x{token:08X} at pos {reader.tell() - 4}"
            )
        print(f"[build] MODEL_START confirmed  pos={reader.tell() - 4}")

        # ── 5. Node tree ───────────────────────────────────────────────────
        read_children(reader, self, model, None)

        return model

    # ── Header ──────────────────────────────────────────────────────────────

    def _load_header(self, reader: ModelInputStream) -> int:
        """
        Mirrors BinaryPersistence.loadHeader().
        Reads all header bytes so the string table is populated before the registry.
        Returns the stream version integer.
        """
        if reader.read_u32() != ModelInputStream.HEADER_START:
            raise RuntimeError("Expected HEADER_START")

        version = reader.read_u32()
        if version == ModelInputStream.STREAM_ID_V1:
            raise RuntimeError("V1 binary format not supported — please re-save models")
        if version not in (_V2, _V3):
            raise RuntimeError(f"Unknown stream version: 0x{version:08X}")

        if version == _V2:
            # readModelReference()  (model id + name — both may call readString)
            self._read_model_reference_v2(reader)
            reader.read_i32()  # model version field (compatibility leftover)
            # Check for optional HEADER_ATTRIBUTES block
            sync = reader.read_u8()
            if sync == ModelInputStream.HEADER_ATTRIBUTES:
                reader.read_bool()  # placeholder boolean (V2)
                props_count = reader.read_i16()
            else:
                # No attributes block — put the byte back logically by adjusting pos
                reader.seek(reader.tell() - 1)
                props_count = 0
        else:
            # V3
            reader.read_module_ref()  # module reference (may be null)
            self._read_model_id(reader)  # model id
            reader.read_string()  # model name
            sync = reader.read_u8()
            if sync != ModelInputStream.HEADER_ATTRIBUTES:
                raise RuntimeError(
                    f"Expected HEADER_ATTRIBUTES (0x{ModelInputStream.HEADER_ATTRIBUTES:02X}), "
                    f"got 0x{sync:02X} at pos {reader.tell() - 1}"
                )
            props_count = reader.read_i16()

        # Optional model properties (key/value pairs)
        for _ in range(props_count):
            reader.read_string()  # key   — adds to string table
            reader.read_string()  # value — adds to string table

        if version == _V3:
            reader.read_u8()  # persistedCapabilities byte

        # HEADER_END marker
        if reader.read_u32() != ModelInputStream.HEADER_END:
            raise RuntimeError("Expected HEADER_END")

        return version

    def _read_model_reference_v2(self, reader: ModelInputStream):
        """
        Consume a V2 SModelReference.

        Byte layout (confirmed from diff.mpb hex):
            kind  u8       — 0x07 for regular uuid-based model id
            uuid  16 bytes — high u64 + low u64
            extra u8       — sub-kind or version byte (0xA1 observed)
            name  string   — long model name (e.g. "jetbrains.mps.vcs.diff")
                             added to string table via read_string()
            null  string   — stereotype or virtual package (0x70 = null)
        """
        kind = reader.read_u8()
        if kind == 0x70:  # NULL model reference
            return
        # Regular model id: uuid (2×u64)
        reader.read_uuid()
        reader.read_u8()  # extra byte after uuid (sub-kind/version)
        reader.read_string()  # model long name — added to string table
        reader.read_string()  # stereotype / virtual package (usually null)

    def _read_model_id(self, reader: ModelInputStream):
        """Consume a V3 SModelId (may be uuid-based or string-based)."""
        kind = reader.read_u8()
        if kind == 0x70:  # NULL
            return
        if kind == 0x48:  # uuid-based
            reader.read_uuid()
        elif kind == 0x47:  # string-based
            reader.read_string()
        # else: silently skip unknown kinds (future-proofing)

    # ── Model properties ─────────────────────────────────────────────────────

    def _load_model_properties(self, reader: ModelInputStream, version: int):
        """
        Mirrors BinaryPersistence.loadModelProperties() for V2 and V3.

        V2 (no dependency format byte):
            loadUsedLanguagesV2  — u16 count, each: uuid + string
            loadModuleRefList    — engaged languages
            loadModuleRefList    — devkits
            loadImports V2       — u32 count, each: model_ref + i32

        V3 (has dependency format byte):
            readByte DEPENDENCY_V1
            loadUsedLanguagesV3  — u16 count, each: readLanguage + i32
            loadEngagedLanguages — u16 count, each: readLanguage
            loadModuleRefList    — devkits
            loadImports V3       — u32 count, each: model_ref (no extra int)
        """
        if version == _V2:
            self._load_used_languages_v2(reader)
            self._load_module_ref_list(reader)  # engaged languages
            self._load_module_ref_list(reader)  # devkits
            self._load_imports(reader, version)
        else:
            dep_fmt = reader.read_u8()
            if dep_fmt != ModelInputStream.DEPENDENCY_V1:
                raise RuntimeError(
                    f"Unknown dependency format: 0x{dep_fmt:02X} at pos {reader.tell() - 1}"
                )
            self._load_used_languages_v3(reader)
            self._load_engaged_languages(reader)
            self._load_module_ref_list(reader)  # devkits
            self._load_imports(reader, version)

    def _load_used_languages_v2(self, reader: ModelInputStream):
        """V2: u16 count, each entry: uuid (2×u64) + string name."""
        count = reader.read_u16()
        print(f"[model_props] used_languages (V2) = {count}")
        for _ in range(count):
            reader.read_uuid()  # language uuid
            reader.read_string()  # language name

    def _load_used_languages_v3(self, reader: ModelInputStream):
        """
        V3: u16 count, each entry: readLanguage() + i32 import version.
        readLanguage() = uuid (2×u64) + string name  (same as V2 per-entry).
        """
        count = reader.read_u16()
        print(f"[model_props] used_languages (V3) = {count}")
        for _ in range(count):
            reader.read_uuid()  # language uuid
            reader.read_string()  # language name
            reader.read_i32()  # import version

    def _load_engaged_languages(self, reader: ModelInputStream):
        """V3 only: u16 count, each: readLanguage() = uuid + string."""
        count = reader.read_u16()
        print(f"[model_props] engaged_languages (V3) = {count}")
        for _ in range(count):
            reader.read_uuid()
            reader.read_string()

    def _load_module_ref_list(self, reader: ModelInputStream):
        """u16 count, each: readModuleReference()."""
        count = reader.read_u16()
        for _ in range(count):
            reader.read_module_ref()

    def _load_imports(self, reader: ModelInputStream, version: int):
        """
        u32 count.
        V2: each = readModelReference() + readInt() (version field).
        V3: each = readModelReference() only.
        """
        count = reader.read_u32()
        print(f"[model_props] imports = {count}")
        for i in range(count):
            model_id = self._read_model_reference(reader)
            if version == _V2:
                reader.read_i32()  # import element version (V2 only)
            self.index_2_imported_model_uuid[str(i + 1)] = model_id or ""
            print(f"[model_props]   import[{i + 1}] id={model_id!r}")

    def _read_model_reference(self, reader: ModelInputStream):
        """
        Reads a SModelReference as written by ModelOutputStream.writeModelReference().
        Returns a best-effort model id string, or None.
        """
        kind = reader.read_u8()

        if kind == 0x70:  # NULL
            return None

        if kind == 0x09:  # MODELREF_INDEX
            reader.read_u32()
            return None

        # Full model reference — kind byte already consumed.
        model_id_kind = reader.read_u8()

        if model_id_kind == 0x48:  # uuid-based SModelId
            uuid = reader.read_uuid()
            model_id = f"r:{uuid[0]:016x}{uuid[1]:016x}"
        elif model_id_kind == 0x70:  # NULL id
            model_id = ""
        else:
            raise RuntimeError(
                f"Unsupported model_id_kind 0x{model_id_kind:02X} at pos {reader.tell()}"
            )

        reader.read_string()  # model name
        return model_id

    # ── Diagnostics ──────────────────────────────────────────────────────────

    def _dump_markers(self, reader: ModelInputStream):
        """Print offsets of all structural markers in the file."""
        markers = {
            ModelInputStream.HEADER_START: "HEADER_START",
            ModelInputStream.HEADER_END: "HEADER_END",
            ModelInputStream.REGISTRY_START: "REGISTRY_START",
            ModelInputStream.REGISTRY_END: "REGISTRY_END",
            ModelInputStream.MODEL_START: "MODEL_START",
        }
        import struct as _struct

        data = reader.data
        print("\n=== Binary marker offsets ===")
        for i in range(len(data) - 3):
            val = _struct.unpack_from(">I", data, i)[0]
            if val in markers:
                print(f"  {markers[val]:20s} @ offset {i}")
        print("=============================\n")

    def _skip_to_marker(self, reader: ModelInputStream, marker: int):
        """
        Sliding-window scan until `marker` (4-byte big-endian) is found and consumed.
        Does NOT call read_string() — only use for sections where string table is irrelevant.
        """
        target = marker.to_bytes(4, "big")
        start = reader.pos
        while reader.pos + 4 <= len(reader.data):
            if reader.data[reader.pos : reader.pos + 4] == target:
                reader.pos += 4
                return
            reader.pos += 1
        raise RuntimeError(f"Marker 0x{marker:08X} not found from pos {start}")
