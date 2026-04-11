from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> int:
    result = subprocess.run(command, cwd=ROOT)
    return result.returncode


def main() -> int:
    commands = [
        [sys.executable, "scripts/build_site_index.py"],
        [sys.executable, "scripts/validate_manifests.py"],
        [sys.executable, "scripts/opportunities/validate_opportunity_outputs.py"],
        [sys.executable, "tests/validate_structure.py"],
        [sys.executable, "tests/validate_docs_presence.py"],
        [sys.executable, "tests/validate_release_hygiene.py"],
    ]
    for command in commands:
        code = run(command)
        if code != 0:
            return code
    print("all validations passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
