# Research memory schemas

Use these schemas as adaptable contracts. Preserve equivalent project-specific names and fields.

## Contents

1. CURRENT.md
2. Evaluation protocol
3. Experiment evidence record
4. Hypothesis registry
5. Durable fact
6. Decision record
7. Claim-evidence matrix
8. Session handoff
9. Provenance snapshot

## 1. CURRENT.md

```markdown
# Current Research State

Last verified: YYYY-MM-DD

## Current question
- RQ ID and one-sentence question

## Authoritative protocol
- Protocol: P...
- Dataset/split:
- Primary metrics:
- Validity warnings:

## Selected evidence
| Purpose | Experiment | Model/artifact | Key result | Protocol | Validity |
|---|---|---|---|---|---|

## Active work
| ID | Status | Job/command | Output path | Resume/check action |
|---|---|---|---|---|

## Current hypotheses and claims
- H...: status, evidence links
- C...: support status, evidence links

## Blockers and open questions
- ...

## Next actions
1. Already decided: ...
2. Optional: ...

## Invalidated/superseded warnings
- Do not use E... because ...; replaced by E...
```

Keep CURRENT short. Link evidence instead of reproducing full history.

## 2. Evaluation protocol

```markdown
# P3 — TIFF metric-depth evaluation

- Status: active
- Version: 3
- Effective date: YYYY-MM-DD
- Supersedes: P2
- Unit of analysis: frame
- Dataset and immutable split/list paths:
- Inclusion/exclusion rules:
- GT source, units, valid range, masking:
- Preprocessing and resize semantics:
- Prediction postprocessing:
- Metrics and exact implementations:
- Alignment: raw / global / per-frame oracle
- Aggregation: macro/micro, mean/median, uncertainty:
- Required sample count and seeds:
- Known limitations:
- Reference script and revision:
- Validation fixtures/sanity checks:
```

Changing GT, masking, split, alignment, aggregation, or metric implementation requires a new protocol version.

## 3. Experiment evidence record

Name files with stable IDs, for example `docs/experiments/E2026-0710-01.md`.

```markdown
# E2026-0710-01 — Short title

## Registry
- Status: completed
- Evidence validity: valid
- Research question: RQ-...
- Hypotheses: H-...
- Protocol: P3
- Supersedes / superseded by:
- Owner and dates:

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
- Working tree dirty: yes/no; diff/patch path:
- Command/launcher:
- Resolved config snapshot:
- Critical config: model/backbone, input size, optimizer, LR, scheduler, epochs/steps, batch size, losses/weights, augmentation, precision
- Environment/hardware: OS, Python, framework/CUDA, GPU
- Dataset, input lists, counts, and hashes:
- Seed(s) and determinism settings:
- Parent checkpoint and output checkpoint:
- Raw artifacts: CSV/JSON/log/predictions
- Evaluation script:

## Key results
| Variant | Split | N | Seed(s) | Primary metric | Secondary metric | Runtime | Notes |
|---|---|---:|---|---:|---:|---:|---|

Include baseline absolute values, aggregation, variability, and units. Add subgroup/error tables when they change the scientific interpretation.

## Observations
- Direct descriptions of the table only.

## Interpretation
- Status: tentative/supported/refuted
- Proposed explanation:
- Alternative explanations:
- Counterevidence and boundary conditions:

## Decision
- Action and rationale:
- What this result does not justify:

## Validity threats
- Leakage, bugs, protocol deviations, missing seeds, selection effects, external validity.

## Follow-ups
- ...
```

## 4. Hypothesis registry

```markdown
## H-012 — Training depth coverage controls far-range calibration
- Status: hypothesis
- Mechanism:
- Predictions:
- Falsifiers:
- Alternative hypotheses:
- Supporting evidence:
- Counterevidence:
- Scope/boundary conditions:
- Next discriminating experiment:
```

## 5. Durable fact

Use “fact” for durable scoped observations, not mechanisms.

```markdown
## F-018 — Shared dual-task latency adds 2.3% under P-latency-1
- Status: valid
- Observation:
- Scope/protocol:
- Evidence: E...
- Key values: depth-only ..., shared ...; N=...
- Boundary conditions:
- Last verified:
```

## 6. Decision record

```markdown
## D-009 — Lead paper tables with raw metric values
- Status: active
- Context:
- Evidence considered:
- Options:
- Decision:
- Consequences and risks:
- Revisit trigger:
- Supersedes / superseded by:
```

## 7. Claim-evidence matrix

```markdown
| Claim ID | Intended wording | Evidence | Protocol/fairness | Counterevidence | Threats | Support | Allowed wording |
|---|---|---|---|---|---|---|---|
| C-01 | ... | E1,E4 | same split | E7 | one seed | partial | “suggests”, not “demonstrates” |
```

Every headline number should resolve to an evidence record and raw artifact.

## 8. Session handoff

```markdown
# YYYY-MM-DD — Session handoff

## Session type
experiment / implementation / diagnosis / planning / writing / literature

## Key Configuration
- Experiment ID and status:
- Model/backbone and parent checkpoint:
- Dataset/splits and N:
- Input/preprocessing:
- Training: epochs/steps, batch, optimizer, LR/scheduler, seed:
- Losses and weights:
- Evaluation protocol:
- Hardware/environment:
- Code revision and dirty state:
- Exact launcher/command:
- Full resolved config:

Use `not applicable` for non-experiment sessions and `unknown / not recorded` for unrecoverable historical fields. Never substitute current defaults.

## Artifact Index
| Artifact | Path | Status/purpose |
|---|---|---|
| Config snapshot | ... | authoritative resolved values |
| Provenance | ... | machine-readable run identity |
| Log | ... | complete/partial |
| Checkpoint | ... | best/final/parent |
| Metrics | ... | raw per-sample/summary |
| Predictions | ... | optional retained outputs |

## Work performed
- ...

## Evidence added or changed
- E... and artifact paths

## Decisions
- D... or “none”

## Running work
| Job | PID/scheduler ID | Command | Log/output | Check/resume action |
|---|---|---|---|---|

## Validity alerts
- ...

## Open questions
- ...

## Exact next actions
1. ...
```

## 9. Provenance snapshot

Prefer saving this beside experiment outputs as `provenance.json`. Extend it for the domain; do not omit unknown fields.

```json
{
  "schema_version": 1,
  "experiment_id": "E2026-0710-02",
  "created_at": "2026-07-10T14:30:00+08:00",
  "status": "running",
  "code": {
    "revision": "<commit>",
    "dirty": true,
    "diff_path": "git_diff.patch"
  },
  "execution": {
    "launcher": "scripts/run.sh",
    "command": "python ...",
    "resolved_config": "config.json",
    "seed": 42
  },
  "data": {
    "dataset": "name/version",
    "train_list": "data/train.txt",
    "eval_list": "data/eval.txt",
    "train_n": 768,
    "eval_n": 240,
    "manifest_hash": "<sha256 or unknown>"
  },
  "protocol": "P-...",
  "environment": {
    "python": "...",
    "framework": "...",
    "cuda": "...",
    "gpu": "..."
  },
  "lineage": {
    "parent_checkpoint": "...",
    "output_checkpoint": "..."
  },
  "artifacts": {
    "log": "train.log",
    "metrics": "eval_metrics.json",
    "predictions": "predictions/"
  }
}
```

### Provenance gate

Before calling an experimental result reproducible, answer all of these:

- Can the exact code state be identified, including uncommitted changes?
- Can the resolved runtime configuration be recovered without consulting current defaults?
- Are dataset, split/list, counts, filtering, and protocol identified?
- Are seed and determinism settings recorded?
- Are parent and output checkpoints distinguishable?
- Are logs, raw metrics, and evaluation scripts indexed?

If any answer is no, preserve the result but label reproducibility `incomplete` and enumerate the missing fields.
