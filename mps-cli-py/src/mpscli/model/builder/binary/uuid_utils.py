# mpscli/model/builder/binary/uuid_utils.py
#
# Pure utility for MPS model UUID formatting.
# No imports - kept dependency-free so it can be imported by any layer
# without risk of circular imports.


def uuid_str(high: int, low: int) -> str:
    # Formats two u64 values as a MPS model uuid string.
    # MPS model UUIDs are prefixed with 'r:' and formatted with dashes,
    # for ex: r:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx and the "r:" prefix distinguishes regular model ids
    return (
        f"r:{high >> 32:08x}-{(high >> 16) & 0xffff:04x}-"
        f"{high & 0xffff:04x}-{(low >> 48) & 0xffff:04x}-"
        f"{low & 0xffffffffffff:012x}"
    )
