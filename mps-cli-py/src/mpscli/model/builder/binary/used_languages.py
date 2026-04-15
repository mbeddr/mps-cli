# mpscli/model/builder/binary/used_languages.py

from mpscli.model.builder.binary.model_input_stream import ModelInputStream
from mpscli.model.builder.binary.constants import STREAM_ID_V2, STREAM_ID_V3

_V2 = STREAM_ID_V2
_V3 = STREAM_ID_V3


def load_used_languages(reader: ModelInputStream, version: int) -> None:
    # mirrors BinaryPersistence.loadUsedLanguages() in:
    # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BinaryPersistence.java
    # and loadUsedLanguagesV3() in the latest master branch after 2024.1
    #
    # Purpose: Reads the used-languages section that records which languages are referencedby this model.
    # In our CLI extraction use case we do not call myModelData.addLanguage() as Java does so we only need to
    # consume and advance past these bytes so the stream position is correct for the sections that follow..
    #
    # V2 format (MPS 2024.1 - the current active format):
    #   u16  count
    #   per entry: 2xu64 UUID + string name
    #
    # V3 format (forward compatibility and does not break anything):
    #   u16  count
    #   per entry: 2xu64 UUID + string name + i32 importVersion

    count = reader.read_u16()

    for _ in range(count):
        # langugage uuid
        reader.read_uuid()
        # language name - string table entry
        reader.read_string()
        if version == _V3:
            # import version integer - only present in V3
            reader.read_i32()
