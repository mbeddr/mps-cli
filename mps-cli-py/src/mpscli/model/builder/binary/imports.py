from mpscli.model.builder.binary.model_input_stream import ModelInputStream

V_2 = ModelInputStream.STREAM_ID_V2


def load_imports(reader: ModelInputStream, builder, version: int) -> None:
    count = reader.read_u32()

    for i in range(count):
        kind = reader.read_u8()
        # NULL model ref
        if kind == 0x70:
            model_id = None
        # MODELREF_INDEX
        elif kind == 0x09:
            reader.read_u32()
            model_id = None
        else:
            # full model reference
            model_id_kind = reader.read_u8()

            if model_id_kind == 0x48:
                uuid = reader.read_uuid()
                model_id = f"r:{uuid[0]:016x}{uuid[1]:016x}"
            elif model_id_kind == 0x70:
                model_id = ""
            else:
                raise RuntimeError(
                    f"Unsupported model_id_kind 0x{model_id_kind:02X} "
                    f"at pos {reader.tell()}"
                )
            # model name
            reader.read_string()

        # V2 import version field
        if version == V_2:
            reader.read_i32()

        builder.index_2_imported_model_uuid[str(i + 1)] = model_id or ""
