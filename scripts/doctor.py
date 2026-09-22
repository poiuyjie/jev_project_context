#!/usr/bin/env python3
"""Read-only structural audit for Project Context V2 research memory."""

from __future__ import annotations

import argparse
import re
from datetime import date, datetime
from pathlib import Path


DATE_RE = re.compile(r"Last (?:verified|updated):\s*(\d{4}-\d{2}-\d{2})", re.I)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def age_days(text: str) -> int | None:
    match = DATE_RE.search(text)
    if not match:
        return None
    try:
        return (date.today() - datetime.strptime(match.group(1), "%Y-%m-%d").date()).days
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="project root")
    parser.add_argument("--stale-days", type=int, default=14)
    args = parser.parse_args()
    root = Path(args.root).resolve()

    critical: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    entry = next((p for p in (root / "AGENTS.md", root / "CLAUDE.md") if p.exists()), None)
    if entry is None:
        warnings.append("missing AGENTS.md/CLAUDE.md operational entry")

    for name in ("CONTEXT.md", "EXPERIMENTS.md"):
        if not (root / name).exists():
            warnings.append(f"missing {name}")

    current = root / "CURRENT.md"
    if not current.exists():
        warnings.append("missing CURRENT.md present-state projection")
    else:
        current_text = read(current)
        age = age_days(current_text)
        if age is None:
            warnings.append("CURRENT.md lacks a parseable Last verified: YYYY-MM-DD")
        elif age > args.stale_days:
            warnings.append(f"CURRENT.md last verified {age} days ago")
        for heading in ("Current question", "Authoritative protocol", "Active work", "Next actions"):
            if not re.search(rf"^##\s+{re.escape(heading)}\s*$", current_text, re.M | re.I):
                notes.append(f"CURRENT.md missing recommended section: {heading}")

    experiments = root / "docs" / "experiments"
    records = sorted(experiments.glob("*.md")) if experiments.exists() else []
    if not records:
        notes.append("no V2 experiment evidence records found under docs/experiments/")
    for path in records:
        text = read(path)
        is_lite = bool(re.search(r"^-\s*Record type:\s*lite\s*$", text, re.M | re.I))
        required_headings = (
            ("Registry", "Provenance", "Key results")
            if is_lite
            else ("Registry", "Provenance", "Key results", "Observations", "Interpretation", "Validity threats")
        )
        missing = [
            heading
            for heading in required_headings
            if not re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.M | re.I)
        ]
        if missing:
            warnings.append(f"{path.relative_to(root)} missing sections: {', '.join(missing)}")
        status_match = re.search(r"^- Status:\s*([^\n]+)", text, re.M | re.I)
        status = status_match.group(1).lower() if status_match else ""
        if any(word in status for word in ("running", "completed")):
            provenance_match = re.search(
                r"^##\s+Provenance\s*$\n(.*?)(?=^##\s+|\Z)", text, re.M | re.S | re.I
            )
            provenance = provenance_match.group(1) if provenance_match else ""
            required_groups = {
                "code revision/dirty state": ("revision", "dirty"),
                "command/launcher": ("command", "launcher"),
                "resolved config": ("config",),
                "dataset/split": ("dataset", "split", "input list", "frame_list", "pairs"),
                "seed": ("seed",),
                "protocol": ("protocol",),
                "checkpoint lineage": ("checkpoint",),
                "log/artifact index": ("log", "artifact"),
            }
            absent = []
            lower = provenance.lower()
            for label, terms in required_groups.items():
                if not any(term in lower for term in terms):
                    absent.append(label)
            if absent:
                warnings.append(
                    f"{path.relative_to(root)} incomplete provenance: {', '.join(absent)}"
                )
            if "provenance.json" not in lower and "config.json" not in lower:
                notes.append(
                    f"{path.relative_to(root)} references no machine-readable "
                    "provenance/config snapshot (provenance.json/config.json)"
                )
        if re.search(r"Evidence validity:\s*(invalidated|superseded)", text, re.I) and not re.search(
            r"superseded[_ ]by|replacement|corrected", text, re.I
        ):
            warnings.append(f"{path.relative_to(root)} is retired without a visible replacement link")

    journals = sorted((root / "docs" / "journal").glob("*.md")) if (root / "docs" / "journal").exists() else []
    legacy_missing = 0
    for path in journals:
        text = read(path)
        if not re.search(r"^###?\s+(Key Findings|关键发现|Observations|Evidence added or changed)", text, re.M | re.I):
            legacy_missing += 1
        session_match = re.search(r"^##\s+Session type\s*$\n(.*?)(?=^##\s+|\Z)", text, re.M | re.S | re.I)
        session_type = session_match.group(1).lower() if session_match else ""
        if "experiment" in session_type or "evaluation" in session_type:
            for heading in ("Key Configuration", "Artifact Index"):
                if not re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.M | re.I):
                    warnings.append(
                        f"{path.relative_to(root)} scientific handoff missing {heading}"
                    )
    if legacy_missing:
        notes.append(f"{legacy_missing}/{len(journals)} journal files lack a recognized evidence/findings anchor")

    exp_index = root / "EXPERIMENTS.md"
    if exp_index.exists():
        age = age_days(read(exp_index))
        if age is None:
            warnings.append("EXPERIMENTS.md lacks a parseable Last updated: YYYY-MM-DD")
        elif age > 30:
            warnings.append(f"EXPERIMENTS.md last updated {age} days ago")

    if any("invalidated" in read(p).lower() for p in records) and not current.exists():
        critical.append("invalidated evidence exists but CURRENT.md cannot warn new sessions")

    print(f"Project Context V2 doctor: {root}")
    for severity, items in (("CRITICAL", critical), ("WARNING", warnings), ("NOTE", notes)):
        for item in items:
            print(f"[{severity}] {item}")
    print(f"Summary: {len(critical)} critical, {len(warnings)} warnings, {len(notes)} notes")
    return 1 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
