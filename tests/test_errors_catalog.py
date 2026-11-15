"""Every user-facing error template in source must appear in docs/errors.md."""
from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COWBELL = ROOT / "cowbell.py"
ERRORS_DOC = ROOT / "docs" / "errors.md"
LAUNCHER = ROOT / "bin" / "cowbell"

# Normalized placeholders: {!r} means repr-formatted slot, {} otherwise.
_MSG = re.compile(r"^\|\s*Message\s*\|\s*`([^`]+)`\s*\|", re.MULTILINE)


def _template(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for piece in node.values:
            if isinstance(piece, ast.Constant):
                parts.append(piece.value)
            elif isinstance(piece, ast.FormattedValue):
                conv = {114: "!r", 115: "!s", 97: "!a"}.get(piece.conversion, "")
                parts.append("{" + conv + "}")
            else:
                parts.append("{}")
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _template(node.left), _template(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def _stderr_print(call: ast.Call) -> bool:
    for kw in call.keywords:
        if kw.arg == "file" and isinstance(kw.value, ast.Attribute) and kw.value.attr == "stderr":
            return True
    return False


def extract_user_error_patterns(path: Path = COWBELL) -> set[str]:
    """Collect stable user-visible error templates from cowbell.py."""
    tree = ast.parse(path.read_text())
    patterns: set[str] = set()

    class Visitor(ast.NodeVisitor):
        def visit_Raise(self, node: ast.Raise) -> None:
            exc = node.exc
            if not isinstance(exc, ast.Call):
                self.generic_visit(node)
                return
            name = getattr(exc.func, "id", None) or getattr(exc.func, "attr", None)
            if name not in ("SystemExit", "SchemaError", "HerdrError", "TypeError") or not exc.args:
                self.generic_visit(node)
                return
            text = _template(exc.args[0])
            if not text:
                self.generic_visit(node)
                return
            if name == "TypeError" and not text.startswith("cowbell:"):
                self.generic_visit(node)
                return
            patterns.add(text)
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Attribute) and node.func.attr == "append":
                base = node.func.value
                if isinstance(base, ast.Name) and base.id in ("problems", "warns") and node.args:
                    text = _template(node.args[0])
                    if text:
                        patterns.add(text)

            if isinstance(node.func, ast.Name) and node.func.id == "print" and node.args:
                arg0 = node.args[0]
                if isinstance(arg0, ast.JoinedStr) and any(
                    isinstance(p, ast.FormattedValue) and isinstance(p.value, ast.Call)
                    and getattr(p.value.func, "id", None) == "trust_note"
                    for p in arg0.values
                ):
                    self.generic_visit(node)
                    return
                text = _template(arg0)
                if text:
                    if _stderr_print(node):
                        if text.startswith("cowbell:") or text.startswith("cowbell "):
                            patterns.add(text)
                    elif text in {
                        "enter <name>",
                        "cowbell adopt --pane ID  (or a sitting name)",
                        "herdr is not installed; nothing to reconcile",
                    }:
                        patterns.add(text)
                    elif "no focused agent pane to adopt" in text:
                        patterns.add(text)
                    elif text.startswith("  unknown harness "):
                        patterns.add("  unknown harness {}")
                    elif "is not installed here" in text and text.strip().startswith("{") or (
                        "is not installed here" in text and "{h['id']}" in ast.unparse(node)
                    ):
                        patterns.add("  {} is not installed here")
                    elif "⊘ refused:" in text:
                        patterns.add("  ⊘ refused: {} on {} is blocked {}")

            self.generic_visit(node)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            if node.name == "trust_note":
                for child in ast.walk(node):
                    if isinstance(child, ast.Return) and child.value:
                        text = _template(child.value)
                        if text:
                            patterns.add(f"cowbell: ! {text}")
            self.generic_visit(node)

    Visitor().visit(tree)

    # herdr() and agent_start use joins the AST does not fold into one literal.
    patterns.add("herdr {} exited {}")
    patterns.add("agent start {} failed")

    # harness verify prints (ANSI styling is not part of the template).
    patterns.update({
        "  target executable/kind is not specified",
        "  binary not found on PATH: {}",
        "  unix user {!r} does not exist on this host",
        "  harness {!r} already exists",
        "  FAIL {}",
        "  {} is not installed here",
    })

    if LAUNCHER.is_file():
        for line in LAUNCHER.read_text().splitlines():
            if line.startswith('echo "cowbell:'):
                m = re.search(r'echo "(.+)"', line)
                if m:
                    patterns.add(m.group(1))

    # Generic HerdrError wrapper at CLI exit.
    patterns.add("cowbell: {}")

    # cmd_adopt builds a multi-line SystemExit from these literals.
    patterns.update({
        "cowbell: no focused agent pane to adopt. Live{}:",
        "cowbell adopt --pane ID  (or a sitting name)",
    })

    return patterns


def catalog_patterns(doc: Path = ERRORS_DOC) -> set[str]:
    text = doc.read_text()
    return set(_MSG.findall(text))


class ErrorsCatalog(unittest.TestCase):
    def test_every_user_error_is_documented(self):
        src = extract_user_error_patterns()
        doc = catalog_patterns()
        missing = sorted(src - doc)
        extra = sorted(doc - src)
        parts = []
        if missing:
            parts.append("undocumented in docs/errors.md:\n" + "\n".join(f"  - `{m}`" for m in missing))
        if extra:
            parts.append("stale entries in docs/errors.md (no longer emitted):\n" + "\n".join(f"  - `{e}`" for e in extra))
        self.assertFalse(parts, "\n\n".join(parts))
