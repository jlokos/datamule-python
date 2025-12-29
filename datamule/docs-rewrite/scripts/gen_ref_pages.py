from __future__ import annotations

import ast
from pathlib import Path

import mkdocs_gen_files

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = PROJECT_ROOT / "datamule"
REFERENCE_ROOT = Path("reference")

nav = mkdocs_gen_files.Nav()
init_modules: dict[Path, ast.Module] = {}
included_modules: set[Path] = set()

def _is_importable(rel_path: Path) -> bool:
    for parent in rel_path.parents:
        if parent == Path("."):
            continue
        if not (PACKAGE_ROOT / parent / "__init__.py").exists():
            return False
    return True


def _has_public_defs(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                return True
    return False


def _has_docstring(tree: ast.Module) -> bool:
    return ast.get_docstring(tree) is not None


def _load_tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


for path in sorted(PACKAGE_ROOT.rglob("*.py")):
    if path.name.startswith("_") and path.name != "__init__.py":
        continue

    rel_path = path.relative_to(PACKAGE_ROOT)
    if rel_path.parts and rel_path.parts[0].startswith("_"):
        continue
    if not _is_importable(rel_path):
        continue
    if path.stat().st_size == 0:
        continue

    if path.name == "__init__.py":
        init_modules[rel_path] = _load_tree(path)
        continue

    tree = _load_tree(path)
    if not _has_public_defs(tree):
        continue

    parts = (*rel_path.parts[:-1], rel_path.stem)
    nav_parts = parts
    rel_doc_path = Path(*parts).with_suffix(".md")
    identifier = ".".join(("datamule",) + parts)

    doc_path = REFERENCE_ROOT / rel_doc_path
    nav[nav_parts] = rel_doc_path.as_posix()
    with mkdocs_gen_files.open(doc_path, "w") as doc_file:
        doc_file.write(f"# {identifier}\n\n::: {identifier}\n")
    mkdocs_gen_files.set_edit_path(doc_path, path)
    included_modules.add(rel_path)

included_packages = {path.parent for path in included_modules}
included_packages.discard(Path("."))

for rel_path, tree in sorted(init_modules.items()):
    parts = rel_path.parent.parts
    if not parts:
        nav_parts = ("datamule",)
        rel_doc_path = Path("index.md")
        identifier = "datamule"
    else:
        nav_parts = parts
        rel_doc_path = Path(*parts, "index.md")
        identifier = ".".join(("datamule",) + parts)

    if rel_path.parent not in included_packages and not _has_docstring(tree) and not _has_public_defs(tree):
        continue

    doc_path = REFERENCE_ROOT / rel_doc_path
    nav[nav_parts] = rel_doc_path.as_posix()
    with mkdocs_gen_files.open(doc_path, "w") as doc_file:
        doc_file.write(f"# {identifier}\n\n::: {identifier}\n")
    mkdocs_gen_files.set_edit_path(doc_path, PACKAGE_ROOT / rel_path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
