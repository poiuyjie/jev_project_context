#!/usr/bin/env python3
"""Optional semantic pre-screen for Project Context V2, backed by TypeSafe Jev.

Second layer of the doctor funnel:

    doctor.py (local regex, free) -> jev_doctor.py (batched semantic triage)
    -> the main model, which reviews the low-confidence items reported here.

Read-only: this script flags suspects, it never writes and never edits
scientific content. Findings are advisory triage, not verdicts. Without
TYPESAFE_API_KEY the script prints a skip note and exits 0, so every
workflow keeps working offline. It always exits 0 (except usage errors);
doctor.py remains the exit-code authority for CI.

Checks per target (positive phrasing: a low probability marks a suspect):

- experiment record: provenance recoverable / headline agrees with the key
  results table / observations kept free of interpretation;
- CURRENT.md: one coherent current state / running work resumable / selected
  evidence values consistent with the referenced records' key results;
- claims registry: support status against the controlled vocabulary, and
  causal language without causal identification.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from jev_client import (
    DEFAULT_MODEL,
    JevError,
    answer_value,
    choice,
    has_api_key,
    noul,
    system_one,
)

STATE_CAP = 24_000
CLAIMS_CAP = 20_000
KEY_RESULTS_CAP = 6_000
CLAIM_LIMIT = 25

CLAIM_SUPPORT = {
    "supported": "Evidence directly supports the claim exactly as worded",
    "partially-supported": "Support exists but is narrower than the wording (scope, seeds, splits)",
    "unsupported": "Evidence does not establish the claim as worded",
    "invalidated": "Supporting evidence was invalidated or superseded",
}

EXPERIMENT_QUESTIONS = {
    "provenance_recoverable": noul(
        "The Provenance section records recoverable concrete values, not merely "
        "'unknown', for command, resolved config, code revision, dataset/split, "
        "seed, and protocol"
    ),
    "headline_matches_table": noul(
        "Every headline result claimed in the Registry or summary agrees with "
        "the Key results table"
    ),
    "observations_are_descriptive": noul(
        "The Observations section contains only direct descriptions of the "
        "table; causal or mechanistic explanation appears only under "
        "Interpretation"
    ),
}

CURRENT_QUESTIONS = {
    "single_current_state": noul(
        "CURRENT describes exactly one coherent present state, without "
        "competing or contradictory current states"
    ),
    "running_work_resumable": noul(
        "Every active or running row in Active work has a concrete resume or "
        "check action"
    ),
    "selected_evidence_consistent": noul(
        "Values in the Selected evidence table are consistent with the "
        "experiment Key results sections appended below"
    ),
}


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)", text, re.M | re.S | re.I
    )
    return match.group(1) if match else ""


def cap(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... [truncated]"


def numeric_probability(value: object) -> float | None:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return None


class Report:
    def __init__(self, min_confidence: float, verbose: bool) -> None:
        self.min_confidence = min_confidence
        self.verbose = verbose
        self.warnings: list[str] = []
        self.reviews: list[str] = []
        self.notes: list[str] = []

    def add_answer(self, target: str, name: str, answer: dict, suspect_below: float) -> None:
        value, confidence = answer_value(answer)
        if value is None:
            self.reviews.append(f"{target} {name}: unparseable answer -> review manually")
            return
        probability = numeric_probability(value)
        label = f"{value!r}" if probability is None else f"p={probability:.2f}"
        conf = f"confidence={confidence:.2f}" if isinstance(confidence, (int, float)) else "confidence=?"
        if probability is not None and probability >= suspect_below:
            if self.verbose:
                print(f"[SEMANTIC-OK] {target} {name}: {label} ({conf})")
            return
        line = f"{target} {name}: {label} ({conf})"
        if confidence is not None and confidence < self.min_confidence:
            self.reviews.append(line + " -> review manually")
        else:
            self.warnings.append(line)

    def summary(self, checked: str) -> list[str]:
        lines = []
        for item in self.warnings:
            lines.append(f"[SEMANTIC-WARNING] {item}")
        for item in self.reviews:
            lines.append(f"[SEMANTIC-REVIEW] {item}")
        for item in self.notes:
            lines.append(f"[NOTE] {item}")
        lines.append(
            f"Summary: {len(self.warnings)} semantic warnings, {len(self.reviews)} review items, {checked}"
        )
        return lines


def ask(report: Report, target: str, state: str, questions: dict, model: str, dry_run: bool) -> bool:
    """Run one System One call; returns False when skipped due to failure."""
    if dry_run:
        print(f"[DRY-RUN] {target}")
        print(json.dumps({"state": cap(state, 400), "model": model, "questions": questions}, indent=2)[:2000])
        return True
    try:
        response = system_one(cap(state, STATE_CAP), questions, model=model)
    except JevError as exc:
        report.notes.append(f"Jev call failed for {target}: {exc}")
        return False
    answers = response.get("answers", {})
    for name in questions:
        report.add_answer(target, name, answers.get(name, {}), suspect_below=0.5)
    return True


def experiment_targets(root: Path, limit: int) -> tuple[list[Path], int]:
    exp_dir = root / "docs" / "experiments"
    records = sorted(exp_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True) if exp_dir.exists() else []
    return records[:limit], max(0, len(records) - len(records[:limit]))


def run_experiments(root: Path, report: Report, args) -> tuple[int, int]:
    targets, skipped = experiment_targets(root, args.limit)
    for path in targets:
        text = read(path)
        if not text.strip():
            continue
        ask(report, str(path.relative_to(root)), text, dict(EXPERIMENT_QUESTIONS), args.model, args.dry_run)
    return len(targets), skipped


def run_current(root: Path, report: Report, args) -> int:
    current = root / "CURRENT.md"
    if not current.exists():
        report.notes.append("no CURRENT.md; semantic current-state check skipped")
        return 0
    text = read(current)
    referenced = sorted(set(re.findall(r"\bE\d{4}-\d{4}-\d{2}\b", text)))
    excerpts, used = [], 0
    missing = []
    for exp_id in referenced:
        record_path = root / "docs" / "experiments" / f"{exp_id}.md"
        if not record_path.exists():
            missing.append(exp_id)
            continue
        key_results = section(read(record_path), "Key results")
        if key_results and used < KEY_RESULTS_CAP:
            excerpts.append(f"### {exp_id} Key results\n{key_results}")
            used += len(key_results)
    if missing:
        report.notes.append(f"CURRENT references records without files: {', '.join(missing)}")
    state = text
    if excerpts:
        state += "\n\n---\n\nReferenced experiment Key results sections:\n\n" + "\n\n".join(excerpts)
    ask(report, "CURRENT.md", state, dict(CURRENT_QUESTIONS), args.model, args.dry_run)
    return len(referenced)


def run_claims(root: Path, report: Report, args) -> int:
    claims_path = root / "docs" / "research" / "claims.md"
    if not claims_path.exists():
        report.notes.append("no docs/research/claims.md; semantic claim check skipped")
        return 0
    text = read(claims_path)
    rows = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and re.fullmatch(r"[A-Z]{1,3}-\d{1,3}", cells[0]):
            rows.append((cells[0], cells[1] if len(cells) > 1 else ""))
    rows = rows[:CLAIM_LIMIT]
    if not rows:
        report.notes.append("no parsable claim rows (expected '| C-01 | wording | ...')")
        return 0
    questions = {}
    for claim_id, _ in rows:
        questions[f"{claim_id}_support"] = choice(
            f"Classify the support status of claim {claim_id} as worded", CLAIM_SUPPORT
        )
        questions[f"{claim_id}_causal"] = noul(
            f"Claim {claim_id} uses causal language (causes, because, due to) without causal identification"
        )
    target = str(claims_path.relative_to(root))
    if args.dry_run:
        print(f"[DRY-RUN] {target} ({len(rows)} claims)")
        print(json.dumps({"state": cap(text, 400), "model": args.model, "questions": questions}, indent=2)[:2000])
        return len(rows)
    try:
        response = system_one(cap(text, CLAIMS_CAP), questions, model=args.model)
    except JevError as exc:
        report.notes.append(f"Jev call failed for {target}: {exc}")
        return len(rows)
    answers = response.get("answers", {})
    for claim_id, _ in rows:
        support = answers.get(f"{claim_id}_support", {})
        value, confidence = answer_value(support)
        if value is None:
            report.reviews.append(f"{target} {claim_id}_support: unparseable answer -> review manually")
        elif value == "supported":
            if args.verbose:
                conf = f"confidence={confidence:.2f}" if isinstance(confidence, (int, float)) else ""
                print(f"[SEMANTIC-OK] {target} {claim_id}_support: supported ({conf})")
        elif confidence is not None and confidence < report.min_confidence:
            report.reviews.append(f"{target} {claim_id}_support: {value} ({confidence=:.2f}) -> review manually")
        else:
            report.warnings.append(f"{target} {claim_id}_support: {value}")
        report.add_answer(target, f"{claim_id}_causal", answers.get(f"{claim_id}_causal", {}), suspect_below=0.5)
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", nargs="?", default=".", help="project root")
    parser.add_argument("--limit", type=int, default=20, help="max experiment records per run (default 20)")
    parser.add_argument("--min-confidence", type=float, default=0.5, help="below this, findings become review items")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--dry-run", action="store_true", help="print the requests that would be sent, call nothing")
    parser.add_argument("--verbose", action="store_true", help="also print passing checks")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not args.dry_run and not has_api_key():
        print("[NOTE] semantic triage skipped: TYPESAFE_API_KEY is not set.")
        print("       The project works fully offline without it; set the key to enable the Jev layer.")
        return 0

    report = Report(min_confidence=args.min_confidence, verbose=args.verbose)
    checked, skipped = run_experiments(root, report, args)
    referenced = run_current(root, report, args)
    claims = run_claims(root, report, args)

    for line in report.summary(
        f"{checked} experiment records checked ({skipped} skipped by limit), "
        f"{referenced} CURRENT evidence links, {claims} claims"
    ):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
