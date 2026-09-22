#!/usr/bin/env python3
"""Task-conditioned context triage for Project Context V2 `start`.

The hottest path of the skill: every session resumes by loading context, and
as the memory tree grows, loading everything is expensive while guessing is
dangerous (acting on invalidated evidence). This script ranks candidate
memory items against the current task with one batched Jev call and emits a
context manifest under a character budget:

    ALWAYS  operational entry + CURRENT.md (navigation, never triaged)
    LOAD    top-ranked items that fit the budget
    SKIP    the rest, kept as one-line pointers
    SURFACE validity warnings (invalidated/superseded), always, even for
            items that were skipped — relevance never hides a staleness alarm

The script never reads files into the conversation and never writes; the
agent reads what the manifest marks LOAD. Without TYPESAFE_API_KEY (or on
API failure) it prints a FALLBACK line and the agent follows the fixed
`start` reading order unchanged.
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
    has_api_key,
    score,
    system_one,
)

STATE_CAP = 24_000
CURRENT_CAP = 6_000
MAX_QUESTIONS = 60
CARD_CAP = 110

RELEVANCE_CRITERIA = [
    "not needed for the current task",
    "background; load only if budget remains",
    "directly needed for the current task",
]

VALIDITY_RE = re.compile(r"^-\s*Evidence validity:\s*(invalidated|superseded)\b.*$", re.M | re.I)
EXP_ID_RE = re.compile(r"\bE\d{4}-\d{4}-\d{2}\b")
HEADING_RE = re.compile(r"^##\s+(?!#)(.+?)\s*$", re.M)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)", text, re.M | re.S | re.I
    )
    return match.group(1) if match else ""


def heading_items(path: Path, text: str) -> list[dict]:
    """Split a registry file into per-heading candidate cards."""
    matches = list(HEADING_RE.finditer(text))
    items = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[match.end() : end]
        heading = match.group(1).strip()
        if heading.lower() == "contents" or not body.strip("-\n "):
            continue
        items.append(
            {
                "path": path,
                "heading": heading,
                "card": f"{path.name} :: {heading[:CARD_CAP]}",
                "chars": len(body),
            }
        )
    return items


def collect_candidates(root: Path) -> list[dict]:
    candidates: list[dict] = []

    for path in sorted((root / "docs" / "experiments").glob("*.md")) if (root / "docs" / "experiments").exists() else []:
        text = read(path)
        if not text.strip():
            continue
        title = re.search(r"^#\s*(" + EXP_ID_RE.pattern + r")\s*[—–-]\s*(.+)$", text, re.M)
        status = re.search(r"^-\s*Status:\s*(.+)$", text, re.M | re.I)
        validity = re.search(r"^-\s*Evidence validity:\s*(\S+)", text, re.M | re.I)
        protocol = re.search(r"^-\s*Protocol:\s*(\S+)", text, re.M | re.I)
        card = f"{path.stem}: {(title.group(2).strip() if title else '')[:CARD_CAP]}"
        card += f" [status: {status.group(1).strip() if status else '?'}"
        card += f", validity: {validity.group(1).strip() if validity else '?'}"
        card += f", protocol: {protocol.group(1).strip() if protocol else '?'}]"
        candidates.append(
            {
                "path": path,
                "heading": None,
                "card": card,
                "chars": len(text),
                "flagged": bool(VALIDITY_RE.search(text)),
            }
        )

    knowledge = root / "docs" / "knowledge"
    for name in ("facts.md", "bugs.md", "decisions.md", "patterns.md"):
        path = knowledge / name
        if path.exists():
            text = read(path)
            items = heading_items(path, text)
            candidates.extend(items if items else [{"path": path, "heading": None, "card": path.name, "chars": len(text), "flagged": False}])

    research = root / "docs" / "research"
    for name in ("hypotheses.md", "claims.md"):
        path = research / name
        if path.exists():
            items = heading_items(path, read(path))
            candidates.extend(items)

    protocols = root / "docs" / "protocols"
    for path in sorted(protocols.glob("*.md")) if protocols.exists() else []:
        text = read(path)
        if text.strip():
            candidates.append({"path": path, "heading": None, "card": f"{path.name} (protocol)", "chars": len(text), "flagged": False})

    journals = root / "docs" / "journal"
    for path in sorted(journals.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True) if journals.exists() else []:
        text = read(path)
        if not text.strip():
            continue
        session = re.search(r"^##\s+Session type\s*$\n(.*?)(?=^##\s+|\Z)", text, re.M | re.S | re.I)
        session_type = first_line(session.group(1)) if session else "?"
        candidates.append(
            {
                "path": path,
                "heading": None,
                "card": f"{path.name} — session: {session_type[:CARD_CAP]}",
                "chars": len(text),
                "flagged": False,
            }
        )

    for candidate in candidates:
        candidate.setdefault("flagged", False)
        candidate.setdefault("heading", None)
    return candidates


def preselect(root: Path, candidates: list[dict], limit: int) -> tuple[list[dict], int]:
    """When over the question cap: keep referenced + validity-flagged items, then recent."""
    current_text = read(root / "CURRENT.md")
    tokens = set(EXP_ID_RE.findall(current_text))
    for candidate in candidates:
        label = candidate["path"].name + (f" :: {candidate['heading']}" if candidate["heading"] else "")
        candidate["referenced"] = any(token in label for token in tokens) or (
            candidate["heading"] is not None and candidate["heading"][:40] in current_text
        )
        candidate.setdefault("mtime", candidate["path"].stat().st_mtime)
    ranked = sorted(candidates, key=lambda c: (not c["referenced"], not c["flagged"], -c["mtime"]))
    return ranked[:limit], max(0, len(candidates) - len(ranked[:limit]))


def build_state(task: str, current_text: str, selected: list[dict]) -> tuple[str, dict]:
    lines = [f"## Task\n{task}"]
    if current_text:
        lines.append(f"## CURRENT.md (navigation)\n{current_text[:CURRENT_CAP]}")
    lines.append("## Candidate memory items")
    questions = {}
    for index, candidate in enumerate(selected):
        key = f"c{index:02d}"
        candidate["key"] = key
        lines.append(f"{key}: {candidate['card']}")
        questions[key] = score("How necessary is this item in the working context right now for the task?", RELEVANCE_CRITERIA)
    return "\n\n".join(lines), questions


def format_item(candidate: dict) -> str:
    target = candidate["path"].name if candidate["heading"] is None else f"{candidate['path'].name} :: {candidate['heading'][:CARD_CAP]}"
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", help="project root")
    parser.add_argument("--task", default="", help="current user request; defaults to CURRENT.md's current question")
    parser.add_argument("--budget-chars", type=int, default=24_000, help="character budget for loaded items")
    parser.add_argument("--max-questions", type=int, default=MAX_QUESTIONS)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--dry-run", action="store_true", help="print inventory and request preview, call nothing")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    current_text = read(root / "CURRENT.md")
    if args.task:
        task = args.task
        task_source = "--task"
    else:
        question = section(current_text, "Current question").strip()
        task = question[:400] if question else "no explicit task; continuing the current question"
        task_source = "CURRENT.md current question"

    candidates = collect_candidates(root)
    always = []
    for name in ("AGENTS.md", "CLAUDE.md"):
        path = root / name
        if path.exists():
            always.append(f"ALWAYS {rel(root, path)} ({len(read(path)):,} chars)")
    if current_text:
        always.append(f"ALWAYS CURRENT.md ({len(current_text):,} chars)")

    validity_surface = []
    for candidate in candidates:
        if candidate["flagged"]:
            match = VALIDITY_RE.search(read(candidate["path"]))
            validity_surface.append(f"SURFACE {format_item(candidate)}: {first_line(match.group(0)) if match else 'validity flag'}")

    selected, dropped = (
        (candidates, 0) if len(candidates) <= args.max_questions else preselect(root, candidates, args.max_questions)
    )
    state, questions = build_state(task, current_text, selected)

    if args.dry_run:
        print(f"# Dry run — task source: {task_source}")
        print(f"# {len(candidates)} candidates, {len(selected)} selected, {dropped} dropped by cap")
        for line in always:
            print(line)
        for line in validity_surface:
            print(line)
        print(json.dumps({"state": state[:1200], "model": args.model, "questions": dict(list(questions.items())[:3])}, indent=2)[:1800])
        return 0

    if not has_api_key():
        print("[FALLBACK] TYPESAFE_API_KEY not set; use the fixed start reading order "
              "(AGENTS.md -> CURRENT.md -> protocol + current records -> EXPERIMENTS key tables -> latest handoff -> on-demand lookups).")
        return 0

    try:
        response = system_one(state[:STATE_CAP], questions, model=args.model)
    except JevError as exc:
        print(f"[FALLBACK] Jev unavailable ({exc}); use the fixed start reading order.")
        return 0

    answers = response.get("answers", {})
    scored = []
    for candidate in selected:
        value, confidence = answer_value(answers.get(candidate.get("key", ""), {}))
        level = int(round(value)) if isinstance(value, (int, float)) else 1
        scored.append((min(max(level, 0), 2), confidence if confidence is not None else 0.0, candidate))

    loaded, skipped = [], []
    remaining = args.budget_chars
    for level, confidence, candidate in sorted(scored, key=lambda x: (-x[0], -x[1])):
        if level >= 1 and candidate["chars"] <= remaining:
            loaded.append((level, confidence, candidate))
            remaining -= candidate["chars"]
        else:
            skipped.append((level, confidence, candidate, "budget" if level >= 1 else "score"))

    print(f"# Context manifest — task source: {task_source}")
    for line in always:
        print(line)
    for level, confidence, candidate in loaded:
        print(f"LOAD {format_item(candidate)} ({candidate['chars']:,} chars) relevance={level} confidence={confidence:.2f}")
    for level, confidence, candidate, reason in skipped:
        print(f"SKIP {format_item(candidate)} relevance={level} confidence={confidence:.2f} ({reason})")
    for line in validity_surface:
        print(line)
    used = sum(c["chars"] for _, _, c in loaded)
    print(
        f"SUMMARY loaded={len(loaded)} ({used:,} of {args.budget_chars:,} chars) "
        f"skipped={len(skipped)} dropped_by_cap={dropped} surfaced={len(validity_surface)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
