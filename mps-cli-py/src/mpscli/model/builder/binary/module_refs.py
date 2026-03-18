from mpscli.model.builder.binary.utils import read_module_reference


def load_module_ref_list(reader):

    count = reader.read_u16()

    for _ in range(count):
        read_module_reference(reader)
