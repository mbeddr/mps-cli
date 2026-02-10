from mpscli.model.builder.binary.utils import read_uuid, read_string


def load_used_languages(reader):
    count = reader.read_u16()
    for _ in range(count):
        read_uuid(reader)
        read_string(reader)
