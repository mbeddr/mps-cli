import keyword

PYTHON_KEYWORDS = set(keyword.kwlist)

def escape_quotes(unescaped_str):
    return unescaped_str.replace('\\', '\\\\').replace('"', '\\"')

def escape_if_python_keyword(unescaped_str):
    if unescaped_str in PYTHON_KEYWORDS:
        return unescaped_str + "_"
    return unescaped_str

def escape_sunder(unescaped_str):
    """
    We need to escape enum values that start and end with an underscore "_" for enums
    as these are reserved for future use by python
    """
    if unescaped_str.startswith('_') and unescaped_str.endswith('_'):
        return "E" + unescaped_str
    return unescaped_str
