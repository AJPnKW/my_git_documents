from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    commands = [
        [sys.executable, "scripts/career/build_career_master.py"],
        [sys.executable, "scripts/career/build_story_master.py"],
        [sys.executable, "scripts/career/activate_career_outputs.py"],
        [sys.executable, "scripts/career/validate_career_outputs.py"],
    ]
    for command in commands:
        run(command)
    print("career pipeline completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
