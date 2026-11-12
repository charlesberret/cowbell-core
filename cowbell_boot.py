"""Console entry for cowbell — checks Python before importing cowbell.py (3.11+ syntax)."""
from __future__ import annotations

import sys


def trap_old_python() -> None:
    if sys.version_info >= (3, 11):
        return
    major, minor, micro = sys.version_info[:3]
    ver = f"{major}.{minor}.{micro}"
    msg = (
        f"cowbell needs Python 3.11 or newer (found {ver} at {sys.executable}). "
        "Install with pipx or Homebrew python."
    )
    print(msg, file=sys.stderr)
    raise SystemExit(2)


def cli() -> None:
    trap_old_python()
    from cowbell import cli as _cli

    _cli()


if __name__ == "__main__":
    cli()
