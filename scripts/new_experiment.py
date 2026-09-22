#!/usr/bin/env python3
"""Scaffold a Project Context V2 experiment evidence record.

Creates docs/experiments/<ID>.md from the canonical schema so records stay
format-stable across sessions instead of drifting. Never overwrites an
existing record. Use --lite for sanity checks and short runs where the full
schema is disproportionate; a lite record can be upgraded to full later.

Examples:
    python3 scripts/new_experiment.py <project-root> "Depth baseline sanity run" --lite
    python3 scripts/new_experiment.py <project-root> "Shared vs depth-only head" \
        --rq RQ-3 --hypotheses H-012 --protocol P3
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

PROVENANCE_CHECKLIST = """\
Provenance gate (fill before interpreting any result):
  command/launcher, resolved config snapshot (config.json + provenance.json
  beside the output), code revision and dirty state, dataset/split and N,
  seeds, protocol version, checkpoint lineage, logs and metrics paths.
  Mark unrecoverable fields 'unknown / not recorded'; never backfill from
  current defaults.
"""


def full_template(exp_id: str, title: str, args) -> str:
    return f"""# {exp_id} — {title}

## Registry
- Status: proposed
- Evidence validity: unchecked
- Research question: {args.rq}
- Hypotheses: {args.hypotheses}
- Protocol: {args.protocol}
- Supersedes / superseded by:
- Owner and dates: {date.today().isoformat()}

## Design
- Purpose:
- Baseline:
- Controlled variables:
- Changed variables:
- Dataset/splits and N:
- Seeds/repetitions:
- Primary metric and acceptance criterion:
- Secondary diagnostics:
- Falsification/stop condition:

## Provenance
- Code revision:
- Working tree dirty: unknown
- Command/launcher:
- Resolved config snapshot:
- Critical config: model/backbone, input size, optimizer, LR, scheduler, epochs/steps, batch size, losses/weights, augmentation, precision
- Environment/hardware:
- Dataset, input lists, counts, and hashes:
- Seed(s) and determinism settings:
- Parent checkpoint and output checkpoint:
- Raw artifacts: CSV/JSON/log/predictions
- Evaluation script:

## Key results
| Variant | Split | N | Seed(s) | Primary metric | Secondary metric | Runtime | Notes |
|---|---|---:|---|---:|---:|---:|---|

## Observations
- (direct descriptions of the table only)

## Interpretation
- Status: hypothesis
- Proposed explanation:
- Alternative explanations:
- Counterevidence and boundary conditions:

## Decision
- Action and rationale:
- What this result does not justify:

## Validity threats
- (leakage, bugs, protocol deviations, missing seeds, selection effects, external validity)

## Follow-ups
- (none)
"""


def lite_template(exp_id: str, title: str, args) -> str:
    return f"""# {exp_id} — {title} (lite)

## Registry
- Record type: lite
- Status: proposed
- Evidence validity: unchecked
- Research question: {args.rq}
- Protocol: {args.protocol}
- Date: {date.today().isoformat()}

## Provenance
- Code revision:
- Command/launcher:
- Resolved config snapshot:
- Dataset/split and N:
- Seed(s):

## Key results
| Variant | Split | N | Seed(s) | Primary metric | Notes |
|---|---|---:|---|---:|---|

## Observation
- (direct description only; upgrade to a full record before interpreting)

## Decision
- Action and rationale:
- What this result does not justify:

## Validity threats
- (none recorded)
"""


def next_experiment_id(root: Path) -> str:
    exp_dir = root / "docs" / "experiments"
    prefix = f"E{date.today():%Y-%m%d}"
    highest = 0
    if exp_dir.exists():
        for path in exp_dir.glob("*.md"):
            match = re.fullmatch(rf"{re.escape(prefix)}-(\d{{2}})", path.stem)
            if match:
                highest = max(highest, int(match.group(1)))
    return f"{prefix}-{highest + 1:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", help="project root")
    parser.add_argument("title", help="short experiment title")
    parser.add_argument("--id", dest="exp_id", help="stable experiment ID (default: auto EYYYY-MMDD-NN)")
    parser.add_argument("--lite", action="store_true", help="lite record for sanity checks and short runs")
    parser.add_argument("--rq", default="—", help="research question ID")
    parser.add_argument("--hypotheses", default="—", help="hypothesis IDs, comma separated")
    parser.add_argument("--protocol", default="—", help="protocol version")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    exp_dir = root / "docs" / "experiments"
    exp_id = args.exp_id or next_experiment_id(root)
    target = exp_dir / f"{exp_id}.md"

    if target.exists():
        print(f"refusing to overwrite existing record: {target}", file=sys.stderr)
        return 1
    if not re.fullmatch(r"E\d{4}-\d{4}-\d{2}", exp_id):
        print(f"ID must match EYYYY-MMDD-NN, got: {exp_id}", file=sys.stderr)
        return 1

    exp_dir.mkdir(parents=True, exist_ok=True)
    template = lite_template if args.lite else full_template
    target.write_text(template(exp_id, args.title, args), encoding="utf-8")
    print(f"created {target} ({'lite' if args.lite else 'full'} record)")
    print(PROVENANCE_CHECKLIST, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
