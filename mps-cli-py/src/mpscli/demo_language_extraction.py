"""
demo_language_extraction.py - extract concept definitions from language structure aspects and
write them as a markdown file that is transferrable to HTML

"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(1, "..")

MODE = "plugins"
PLUGINS_PATH = r"C:\Temp\plugins"
TEST_PROJECT = r"..\..\mps_test_projects\mps_cli_binary_persistency_language"
OUTPUT_FILE = Path(f"language_concepts_{datetime.now().strftime('%H%M%S')}.md")

from mpscli.model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder
from mpscli.model.builder.SLanguageBuilder import SLanguageBuilder


def _short(full_name: str) -> str:
    if not full_name:
        return ""
    return full_name.split(".")[-1]


def _prop(node, key: str, default="") -> str:
    props = getattr(node, "properties", None) or {}
    return props.get(key, default).strip()


def _ref_resolve_info(ref_obj) -> str:
    return (getattr(ref_obj, "resolve_info", None) or "").strip()


def extract_concept_info(concept_node) -> dict:
    # pull all useful fields from a ConceptDeclaration or InterfaceConceptDeclaration SNode
    info = {}

    info["name"] = _prop(concept_node, "name") or _short(
        str(getattr(concept_node, "concept", ""))
    )

    info["concept_type"] = _short(str(getattr(concept_node, "concept", "") or ""))
    info["is_abstract"] = _prop(concept_node, "abstract") == "true"
    info["is_root"] = _prop(concept_node, "rootable") == "true"
    info["alias"] = _prop(concept_node, "alias")
    info["short_description"] = _prop(concept_node, "shortDescription")

    # supertype is a direct reference on the root node
    refs = getattr(concept_node, "references", None) or {}
    extends_ref = refs.get("extends") or refs.get("superConcept")
    info["extends"] = _ref_resolve_info(extends_ref) if extends_ref else ""

    implements = []
    properties = []
    child_links = []
    ref_links = []

    for child in getattr(concept_node, "children", None) or []:
        role = getattr(child, "role_in_parent", "") or ""
        child_refs = getattr(child, "references", None) or {}

        if role == "implements":
            ri = (
                _ref_resolve_info(child_refs.get("intfc"))
                if "intfc" in child_refs
                else ""
            )
            if ri:
                implements.append(ri)

        elif role == "propertyDeclaration":
            prop_name = _prop(child, "name")
            prop_type = (
                _ref_resolve_info(child_refs.get("dataType"))
                if "dataType" in child_refs
                else ""
            )
            if prop_name:
                properties.append({"name": prop_name, "type": prop_type})

        elif role == "linkDeclaration":
            meta = _prop(child, "metaClass")
            link_name = _prop(child, "role")
            raw_card = _prop(child, "sourceCardinality")
            cardinality = raw_card.split("/")[-1] if "/" in raw_card else raw_card
            link_type = (
                _ref_resolve_info(child_refs.get("target"))
                if "target" in child_refs
                else ""
            )

            if not link_name:
                continue

            entry = {"name": link_name, "type": link_type, "cardinality": cardinality}
            if "aggregation" in meta:
                child_links.append(entry)
            elif "reference" in meta:
                ref_links.append(entry)

    info["implements"] = implements
    info["properties"] = properties
    info["child_links"] = child_links
    info["ref_links"] = ref_links

    return info


def _format_concept(info: dict) -> str:
    # produces the plain-text declaration block usedd for .md file
    lines = []

    prefix = "abstract " if info["is_abstract"] else ""
    concept_kind = (
        "interface concept" if "Interface" in info["concept_type"] else "concept"
    )
    header = f"{prefix}{concept_kind} {info['name']}"

    extends_part = f"extends {_short(info['extends'])}" if info["extends"] else ""
    impl_parts = [_short(i) for i in info["implements"]]

    if extends_part and impl_parts:
        lines.append(f"{header} - {extends_part}")
        pad = " " * (len(header) + 3)
        for iface in impl_parts:
            lines.append(f"{pad}implements {iface}")
    elif extends_part:
        lines.append(f"{header} - {extends_part}")
    elif impl_parts:
        lines.append(f"{header} - implements {impl_parts[0]}")
        pad = " " * (len(header) + 3)
        for iface in impl_parts[1:]:
            lines.append(f"{pad}implements {iface}")
    else:
        lines.append(header)

    if info["alias"] or info["short_description"] or info["is_root"]:
        lines.append("")
    if info["alias"]:
        lines.append(f"alias: {info['alias']}")
    if info["short_description"]:
        lines.append(f"description: {info['short_description']}")
    if info["is_root"]:
        lines.append("instance can be root: yes")

    if info["properties"]:
        lines.append("")
        lines.append("properties:")
        for p in info["properties"]:
            t = f" : {_short(p['type'])}" if p["type"] else ""
            lines.append(f"  {p['name']}{t}")

    if info["child_links"]:
        lines.append("")
        lines.append("children:")
        for c in info["child_links"]:
            t = f" : {_short(c['type'])}" if c["type"] else ""
            card = f" [{c['cardinality']}]" if c["cardinality"] else ""
            lines.append(f"  {c['name']}{t}{card}")

    if info["ref_links"]:
        lines.append("")
        lines.append("references:")
        for r in info["ref_links"]:
            t = f" : {_short(r['type'])}" if r["type"] else ""
            card = f" [{r['cardinality']}]" if r["cardinality"] else ""
            lines.append(f"  {r['name']}{t}{card}")

    return "\n".join(lines)


def collect_languages_with_structure() -> list:
    result = []
    for lang in sorted(SLanguageBuilder.languages.values(), key=lambda l: l.name):
        if not lang.models:
            continue
        structure = lang.find_model_by_name("structure")
        if structure and structure.root_nodes:
            result.append((lang, structure))
    return result


def build_markdown(languages_with_structure: list) -> str:
    # the markdown uses fencedd code blocks so thhe aligned plain text declaration renders in monospace
    # in HTML but is still clean as raww text
    sections = []

    sections.append("# Language Concept Definitions")
    sections.append("")
    sections.append("only languages for which a .mpl source was found are included.")
    sections.append("")

    if not languages_with_structure:
        sections.append("No structure aspect models were found.")
        return "\n".join(sections)

    for lang, structure in languages_with_structure:
        sections.append(f"## {lang.name}")
        sections.append("")
        sections.append(f"uuid: {lang.uuid}  ")
        sections.append(f"version: {lang.language_version}  ")
        sections.append(f"concepts: {len(structure.root_nodes)}")
        sections.append("")

        for root in structure.root_nodes:
            cname = _short(str(getattr(root, "concept", "") or ""))
            if "concept" not in cname.lower() and "Concept" not in cname:
                continue
            info = extract_concept_info(root)
            if not info["name"]:
                continue
            # fenced code block preserves alignment and I think renders cleanly in HTML
            sections.append("```")
            sections.append(_format_concept(info))
            sections.append("```")
            sections.append("")

    return "\n".join(sections)


def main():
    path = PLUGINS_PATH if MODE == "plugins" else TEST_PROJECT

    print(f"Parsing ({MODE}): {path}", flush=True)
    builder = SSolutionsRepositoryBuilder()
    builder.USE_CACHE = False
    builder.build(path)

    languages_with_structure = collect_languages_with_structure()

    print(
        f"Languages with structure aspect: {len(languages_with_structure)}", flush=True
    )

    for lang, structure in languages_with_structure:
        print(f"\n{'=' * 60}")
        print(f"Language : {lang.name}")
        print(f"uuid     : {lang.uuid}")
        print(f"version  : {lang.language_version}")
        print(f"concepts : {len(structure.root_nodes)}")
        print(f"{'=' * 60}")
        print("")

        for root in structure.root_nodes:
            cname = _short(str(getattr(root, "concept", "") or ""))
            if "concept" not in cname.lower() and "Concept" not in cname:
                continue
            info = extract_concept_info(root)
            if not info["name"]:
                continue
            # print each line indented by two spaces for readabilityy
            for line in _format_concept(info).splitlines():
                print(f"  {line}")
            print("")

    md = build_markdown(languages_with_structure)
    OUTPUT_FILE.write_text(md, encoding="utf-8")
    print(f"\nmarkdown file written: {OUTPUT_FILE}", flush=True)


if __name__ == "__main__":
    main()
