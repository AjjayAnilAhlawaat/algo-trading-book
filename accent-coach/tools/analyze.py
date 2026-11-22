#!/usr/bin/env python3
"""Spec ↔ tasks ↔ tests traceability check (the Spec Kit `analyze` step, automated).

Fails when:
  * a task marked [x] cites an EARS id (e.g. "(E001-04)") that no test references;
  * a test or task cites an EARS id that does not exist in any spec;
  * a spec lacks an "Out of scope" section.
Warns (no failure) for requirements not yet covered by any test.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EARS = re.compile(r"\bE(\d{3})-(\d{2})\b")
# Only real tests count: Rust/Python `test_e001_04_*` names, Dart `test('E004-01 ...')` descriptions.
TEST_ID = re.compile(r"test_e(\d{3})_(\d{2})|test\(\s*['\"]E(\d{3})-(\d{2})")
TEST_GLOBS = ["packages/**/*.rs", "services/**/tests/*.py", "apps/**/test/**/*.dart"]


def norm(m: re.Match) -> str:
    g = [x for x in m.groups() if x is not None]
    return f"E{g[0]}-{g[1]}"


def main() -> int:
    errors: list[str] = []
    spec_ids: dict[str, str] = {}
    for spec in sorted(ROOT.glob("specs/*/spec.md")):
        text = spec.read_text("utf-8")
        for line in text.splitlines():
            if line.startswith("| E"):
                m = EARS.search(line)
                if m:
                    spec_ids[norm(m)] = spec.parent.name
        if "## Out of scope" not in text:
            errors.append(f"{spec.relative_to(ROOT)}: missing '## Out of scope'")

    tested: set[str] = set()
    for g in TEST_GLOBS:
        for f in ROOT.glob(g):
            if "target" in f.parts:
                continue
            for m in TEST_ID.finditer(f.read_text("utf-8")):
                rid = norm(m)
                tested.add(rid)
                if rid not in spec_ids:
                    errors.append(f"{f.relative_to(ROOT)}: cites unknown requirement {rid}")

    for tasks in sorted(ROOT.glob("specs/*/tasks.md")):
        for line in tasks.read_text("utf-8").splitlines():
            done = line.lstrip().startswith("- [x]")
            for m in EARS.finditer(line):
                rid = norm(m)
                if rid not in spec_ids:
                    errors.append(f"{tasks.relative_to(ROOT)}: cites unknown requirement {rid}")
                elif done and rid not in tested:
                    errors.append(f"{tasks.relative_to(ROOT)}: task done but {rid} has no test")

    untested = sorted(set(spec_ids) - tested)
    by_spec: dict[str, list[str]] = {}
    for rid in untested:
        by_spec.setdefault(spec_ids[rid], []).append(rid)

    covered = len(spec_ids) - len(untested)
    print(f"requirements: {len(spec_ids)}  with tests: {covered}  ({covered / max(len(spec_ids), 1):.0%})")
    for spec, ids in by_spec.items():
        print(f"  pending  {spec}: {', '.join(ids)}")
    for e in errors:
        print(f"  ERROR    {e}")
    print("ANALYZE:", "FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
