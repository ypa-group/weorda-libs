"""weorda-ids must stay stdlib-only: it is imported from shared_kernel/."""

# ===== Standard Library =====
import ast
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "src" / "weorda_ids"


def _imported_top_levels() -> set[str]:
    found: set[str] = set()
    for module_path in PACKAGE_ROOT.rglob("*.py"):
        tree = ast.parse(module_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                found.add(node.module.split(".")[0])
    return found


def test_package_imports_only_stdlib_and_itself() -> None:
    allowed = set(sys.stdlib_module_names) | {"weorda_ids"}
    violations = _imported_top_levels() - allowed
    assert not violations, f"non-stdlib imports in weorda-ids: {sorted(violations)}"
