from mpscli.model.builder.binary.utils import read_module_reference


def load_module_ref_list(reader):
    # mirrors BinaryPersistence.loadModuleRefList() in:
    # https://github.com/JetBrains/MPS/blob/6236c4073eac3cde78506add6b0fa90601d76009/core/persistence/source/jetbrains/mps/persistence/binary/BinaryPersistence.java
    count = reader.read_u16()

    for _ in range(count):
        read_module_reference(reader)
