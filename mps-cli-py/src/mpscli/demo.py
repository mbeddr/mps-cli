"""
demo.py - A quick local test for the binary parser.

Points at a local MPS project directory and prints a summary of what was parsed.
Edit PLUGINS_PATH below to point at either MPS plugins folder or a test project.

Two modes:
    MODE = "plugins": parse a full MPS plugins directory (e.g. C:\\Temp\\plugins)
    MODE = "test_project": parse a single mps_test_projects directory (original behaviour)
"""

import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(1, "..")

# "plugins" or "test_project"
MODE = "plugins"
PLUGINS_PATH = r"C:\Temp\plugins"
TEST_PROJECT = r"..\..\mps_test_projects\mps_cli_lanuse_file_per_root"

from mpscli.model.builder.SSolutionsRepositoryBuilder import SSolutionsRepositoryBuilder


def count_nodes(node) -> int:
    total = 1
    for child in node.children or []:
        total += count_nodes(child)
    return total


def concept_name(concept) -> str:
    if concept is None:
        return "<null>"
    if isinstance(concept, str):
        return concept
    full = getattr(concept, "name", None)
    if full:
        return full.split(".")[-1]
    return str(concept)


def concept_full_name(concept) -> str:
    if concept is None:
        return "<null>"
    if isinstance(concept, str):
        return concept
    return getattr(concept, "name", str(concept))


def fmt_id(value) -> str:
    return str(value) if value is not None else "null"


def print_node(node, depth: int = 0, max_depth: int = 3) -> None:
    if depth > max_depth:
        return

    pad = "  " * depth
    cname = concept_name(node.concept)
    role = getattr(node, "role_in_parent", None)
    uid = fmt_id(getattr(node, "uuid", None))
    name = node.properties.get("name", "")

    # node headline: bullet + concept + role slot + name in quotes + id in brackets
    role_tag = f" [{role}]" if role else ""
    name_tag = f"  '{name}'" if name else ""
    print(f"{pad}\u2022 {cname}{role_tag}{name_tag}  [{uid}]")

    # other properties (name already shown inline above)
    for k, v in sorted((node.properties or {}).items()):
        if k != "name":
            print(f"{pad}    {k} = {v!r}")

    # references
    for k, ref in sorted((node.references or {}).items()):
        resolve = getattr(ref, "resolve_info", None) or ""
        model_u = str(getattr(ref, "model_uuid", "") or "")
        if model_u.startswith("java:"):
            # java stub reference - show class name from resolve_info
            print(f"{pad}    {k} -> {resolve} (Java)")
        else:
            # mps model reference - show uuid + resolve hint
            hint = f" ({resolve})" if resolve else ""
            print(f"{pad}    {k} -> {model_u[:36]}{hint}")

    for child in node.children or []:
        print_node(child, depth + 1, max_depth)


def print_model(model, max_roots: int = 3, max_depth: int = 3) -> None:
    roots = model.root_nodes
    total_nodes = sum(count_nodes(r) for r in roots)

    print(f"\n--- Model: {model.name} ---")
    print(f"    uuid       : {model.uuid}")
    print(f"    root nodes : {len(roots)}")
    print(f"    total nodes: {total_nodes}")

    for i, root in enumerate(roots[:max_roots]):
        print(f"\n  [ROOT {i}]")
        print_node(root, depth=2, max_depth=max_depth)

    if len(roots) > max_roots:
        print(f"\n  ... ({len(roots) - max_roots} more root nodes not shown)")


def verify_model(model) -> dict:
    checks = {}

    checks["uuid_set"] = (
        model.uuid not in ("r:unknown", "", None),
        str(model.uuid),
    )
    checks["name_set"] = (
        model.name not in ("unknown.model", "", None),
        str(model.name),
    )

    bad_concepts = [
        concept_full_name(r.concept) for r in model.root_nodes if not r.concept
    ]
    checks["concepts_set"] = (
        not bad_concepts,
        f"{len(bad_concepts)} missing" if bad_concepts else "all set",
    )

    null_ids = sum(1 for r in model.root_nodes if getattr(r, "uuid", None) is None)
    checks["node_ids_set"] = (
        null_ids == 0,
        f"{null_ids} null ids" if null_ids else "all set",
    )

    bad_props = sum(
        1
        for r in model.root_nodes
        if not isinstance(getattr(r, "properties", None), dict)
    )
    checks["properties_are_dict"] = (
        bad_props == 0,
        f"{bad_props} nodes with bad props" if bad_props else "all dicts",
    )

    bad_refs = sum(
        1
        for r in model.root_nodes
        if not isinstance(getattr(r, "references", None), dict)
    )
    checks["references_are_dict"] = (
        bad_refs == 0,
        f"{bad_refs} nodes with bad refs" if bad_refs else "all dicts",
    )

    return checks


def print_languages(repo) -> None:
    # split languagess into two groups so basically those with aspect models loaded (mpl was actuallyy found) and
    # those without (maybe only seen via registry during .mpb parsing)
    with_models = [l for l in repo.languages if l.models]
    without_models = [l for l in repo.languages if not l.models]

    print(f"\n*** Languages ({len(repo.languages)} total) ***")
    print(f"  with aspect models loaded - {len(with_models)}")
    print(f"  Registry-only (no .mpl found) : {len(without_models)}")

    if with_models:
        print("\n  ---Languages with aspect models ----")
        for lang in sorted(with_models, key=lambda l: l.name):
            aspect_names = ", ".join(
                m.name.split(".")[-1] for m in lang.models if m.name
            )
            print(f"  \u2022 {lang.name}")
            print(f"  version : {lang.language_version}")
            print(f"  uuid    : {lang.uuid}")
            print(f"  aspects : {aspect_names}")
            print(f"  concepts (registry): {len(lang.concepts)}")

            # show rooot node countt per aspect to verify .mpb parsing actually worked
            for m in lang.models:
                aspect = m.name.split(".")[-1] if m.name else "?"
                root_count = len(m.root_nodes)
                print(f"[{aspect}] {root_count} roots")

                if "structure" in (m.name or "") and root_count > 0:
                    concept_names = [
                        r.properties.get("name", "")
                        for r in m.root_nodes[:5]
                        if r.properties.get("name")
                    ]
                    if concept_names:
                        print(f"sample concepts: {', '.join(concept_names)}")

    if without_models:
        print("\n  ---- Registry-only languages (no aspect models) ---")
        for lang in sorted(without_models, key=lambda l: l.name):
            print(f"  \u2022 {lang.name}  ({len(lang.concepts)} concepts)")


def main() -> None:
    path = PLUGINS_PATH if MODE == "plugins" else TEST_PROJECT

    builder = SSolutionsRepositoryBuilder()

    msg = f"Parsing ({MODE}): {path}"
    print(msg, flush=True)
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

    t0 = time.perf_counter()
    repo = builder.build(path)
    t1 = time.perf_counter()

    elapsed = t1 - t0
    timing_msg = f"Parsing complete in {elapsed:.1f}s"
    print(f"\n{timing_msg}")
    sys.stderr.write(timing_msg + "\n")
    sys.stderr.flush()

    total_models = sum(len(s.models) for s in repo.solutions)
    total_nodes = sum(
        sum(count_nodes(r) for r in m.root_nodes)
        for s in repo.solutions
        for m in s.models
    )

    summary = (
        f"\n***Repository Summary***\n"
        f"  Solutions : {len(repo.solutions)}\n"
        f"  Languages : {len(repo.languages)}\n"
        f"  Models    : {total_models}\n"
        f"  Nodes     : {total_nodes:,}\n"
    )
    print(summary)
    sys.stderr.write(summary)
    sys.stderr.flush()

    print("=== Verification ===")
    failed = 0
    for sol in repo.solutions:
        for model in sol.models:
            checks = verify_model(model)
            bad = [(k, detail) for k, (passed, detail) in checks.items() if not passed]
            if bad:
                failed += 1
                print(f"  FAIL  {model.name}")
                for k, detail in bad:
                    print(f"        [{k}] {detail}")

    verdict = (
        f"  All {total_models} models passed verification"
        if failed == 0
        else f"  {failed} models failed verification"
    )
    print(verdict)
    sys.stderr.write(f"\n{verdict}\n")
    sys.stderr.flush()

    # language extension verification - shows whether .mpl reading worked
    print_languages(repo)

    print("\n=== Solutions ===")
    for sol in repo.solutions:
        if not sol.models:
            # skip language-only jars with no models to show
            continue
        sol_nodes = sum(sum(count_nodes(r) for r in m.root_nodes) for m in sol.models)
        print(f"\n{'='*60}")
        print(f"Solution : {sol.name}")
        print(f"Models   : {len(sol.models)}   Nodes: {sol_nodes:,}")
        print(f"{'='*60}")
        for model in sol.models:
            print_model(model, max_roots=3, max_depth=3)


if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()

    # redirect stdout to a log file
    log_file = f"mps_debug_{datetime.now().strftime('%H%M%S')}.log"
    sys.stdout = open(log_file, "w", encoding="utf-8", buffering=1)
    print(f"Logging to: {log_file}")

    main()
