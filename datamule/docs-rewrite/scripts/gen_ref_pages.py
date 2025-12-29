from __future__ import annotations

from pathlib import Path

import mkdocs_gen_files

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = PROJECT_ROOT / "datamule"
REFERENCE_ROOT = Path("reference")

nav = mkdocs_gen_files.Nav()

def _is_importable(rel_path: Path) -> bool:
    for parent in rel_path.parents:
        if parent == Path("."):
            continue
        if not (PACKAGE_ROOT / parent / "__init__.py").exists():
            return False
    return True


for path in sorted(PACKAGE_ROOT.rglob("*.py")):
    if path.name.startswith("_") and path.name != "__init__.py":
        continue

    rel_path = path.relative_to(PACKAGE_ROOT)
    if rel_path.parts and rel_path.parts[0].startswith("_"):
        continue
    if not _is_importable(rel_path):
        continue

    if path.name == "__init__.py":
        parts = rel_path.parent.parts
        if not parts:
            nav_parts = ("datamule",)
            rel_doc_path = Path("index.md")
            identifier = "datamule"
        else:
            nav_parts = parts
            rel_doc_path = Path(*parts, "index.md")
            identifier = ".".join(("datamule",) + parts)
    else:
        parts = (*rel_path.parts[:-1], rel_path.stem)
        nav_parts = parts
        rel_doc_path = Path(*parts).with_suffix(".md")
        identifier = ".".join(("datamule",) + parts)

    doc_path = REFERENCE_ROOT / rel_doc_path
    nav[nav_parts] = rel_doc_path.as_posix()
    with mkdocs_gen_files.open(doc_path, "w") as doc_file:
        doc_file.write(f"# {identifier}\n\n::: {identifier}\n")
    mkdocs_gen_files.set_edit_path(doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
