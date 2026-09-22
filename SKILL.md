---
name: project-context-v2
description: Manage evidence-first memory across the full lifecycle of long-term scientific research and research engineering. Use when initializing a research project or adopting the memory system into an existing one, resuming work across AI sessions, formulating questions and hypotheses, planning or registering experiments, recording running/completed/failed experiments, preserving raw key tables and provenance, correcting invalid analyses, promoting findings into knowledge, auditing claim support, handing off work, or diagnosing documentation drift without losing reproducibility.
---

# Project Context V2

Maintain research memory as a traceable chain from question to evidence to claim. Preserve measurements and provenance before interpretation so a later correction can replace the analysis without destroying the record.

## Non-negotiable rules

1. Treat evidence as more durable than interpretation. When space is limited, remove repetitive prose before removing key tables, sample counts, protocols, baselines, uncertainty, failure cases, or artifact paths.
2. Never silently rewrite history. Mark a result or claim `superseded` or `invalidated`, state why, and link its replacement.
3. Separate four epistemic classes:
   - **Evidence**: observed values and artifacts.
   - **Observation**: description directly supported by evidence.
   - **Interpretation**: causal or mechanistic explanation that may be wrong.
   - **Decision**: action chosen under stated evidence, constraints, and risk.
4. Never convert missing, incomparable, or failed measurements into conclusions. Use `—`, `not measured`, `failed`, or `incomparable` explicitly.
5. Keep raw or per-sample data in machine-readable artifacts when available. Preserve the decisive subset as Markdown tables so the project remains understandable if outputs are unavailable.
6. Record negative results, bugs, leakage, protocol changes, and counterexamples with the same care as improvements.
7. Do not claim causality from correlation, ablation-free comparisons, changed protocols, or cherry-picked samples.
8. Read before writing. Preserve user changes and request confirmation before changing scientific ground truth when evidence is ambiguous.
9. Treat configuration as evidence. A result without recoverable command, resolved config, code revision, data split, seed, protocol, and artifact index is not fully reproducible; mark missing fields `unknown`, never infer historical values from current defaults.

## Canonical memory model

Use the following default layout. Adapt existing names instead of duplicating equivalent files.

```text
project/
├── AGENTS.md or CLAUDE.md      # operational entry: environment, commands, constraints, map
├── CONTEXT.md                  # stable identity, terminology, research scope
├── CURRENT.md                  # authoritative present-state projection
├── EXPERIMENTS.md              # compact experiment registry and decisive tables
└── docs/
    ├── architecture.md         # system/research pipeline overview
    ├── protocols/              # datasets, splits, metrics, evaluation versions
    ├── research/
    │   ├── questions.md        # research questions and success criteria
    │   ├── hypotheses.md       # hypotheses and falsification conditions
    │   └── claims.md           # claims mapped to evidence and threats
    ├── knowledge/
    │   ├── facts.md            # durable observations with evidence links
    │   ├── bugs.md             # validity-impacting and implementation bugs
    │   ├── decisions.md        # ADRs and research decisions
    │   └── patterns.md         # reproducible implementation/analysis patterns
    ├── experiments/            # one evidence record per stable experiment ID
    ├── journal/                # chronological session narrative and handoffs
    └── archive/                # optional retired snapshots; never the current truth
```

`CURRENT.md` is a projection, not a second history. Keep only the current question, authoritative protocol, selected models/results, running work, blockers, next actions, and invalidated warnings needed to resume safely.

Read [references/schemas.md](references/schemas.md) before creating or materially changing these files. Read [references/lifecycle.md](references/lifecycle.md) when planning, recording, correcting, synthesizing, or writing research.

## Select an operation

Map the request to one operation. Combine operations only when the user asks for an end-to-end action.

| Request | Operation | Default mutation |
|---|---|---|
| initialize research memory | `init` | create missing files only |
| load context / continue work | `start` | read-only |
| formulate question or hypothesis | `frame` | update research records with confirmation |
| plan/register an experiment | `plan` | create proposed experiment record |
| record progress or results | `record` | append evidence; update status |
| close session / handoff | `end` | write journal and refresh CURRENT |
| correct a bugged result or conclusion | `correct` | preserve old record; link replacement |
| synthesize stable knowledge | `synthesize` | promote evidence-backed observations |
| audit claim support | `claim-audit` | read-only unless asked to update |
| check memory/document health | `doctor` | read-only |

## Operation workflows

### `init`

1. Inspect existing files and project conventions.
2. Ask only for missing high-impact information: research objective, unit of analysis, datasets, primary metrics, acceptance criteria, compute constraints, and target outputs.
3. Create only missing structure. Never overwrite populated files.
4. Seed `CURRENT.md` with unknowns explicitly marked, not invented.
5. Establish a versioned evaluation protocol before recording headline metrics.

### `start`

If `TYPESAFE_API_KEY` is set, first run `python3 scripts/jev_context.py <project-root> --task "<the user's request>"` and use its manifest: read `LOAD` items in full, treat `SKIP` items as pointers for on-demand lookup only, and relay every `SURFACE` validity line to the user even when the item was skipped (see *Optional Jev layers*). Then read, in this order:

1. Operational entry file (`AGENTS.md` or `CLAUDE.md`).
2. `CURRENT.md` if present. Treat it as a navigation aid, then verify its headline values against evidence records.
3. Active evaluation protocol and current experiment records.
4. Relevant key tables in `EXPERIMENTS.md`; do not replace them with prose summaries.
5. Latest handoff/open questions.
6. Relevant facts, bugs, decisions, hypotheses, and claims on demand.

Report:

- authoritative current state and its evidence paths;
- active/running work and exact resume command when known;
- unresolved validity threats or conflicting records;
- next actions, distinguishing already-decided work from optional suggestions.

Do not present historical interpretation as current fact merely because it appears in a recent journal.

### `frame`

1. State the research question, unit of analysis, scope, and success criteria.
2. Register hypotheses with mechanism, predictions, alternatives, falsifiers, and required evidence.
3. Identify confounders, leakage risks, and measurement limitations before experiments.
4. Distinguish exploratory from confirmatory work.
5. Avoid committing to a method before specifying what observation would disprove it.

### `plan`

1. Assign a stable experiment ID such as `E2026-0710-01`.
2. Record status `proposed` or `ready`, research question, hypothesis IDs, baseline, controlled variables, changed variables, dataset/split, seeds, primary/secondary metrics, acceptance and falsification criteria, artifacts, compute estimate, and stop conditions.
3. Freeze or version the evaluation protocol. If it changes later, results are not directly comparable without an explicit bridge.
4. Include sanity checks and failure diagnostics.
5. Prevent result-aware acceptance criteria.

### `record`

Scaffold new records with `python3 scripts/new_experiment.py <project-root> "<title>"` from this skill directory; add `--lite` for sanity checks and short runs (Registry, Provenance, Key results, Observation, Decision, Validity threats only — upgrade to a full record before interpreting). Then:

1. Determine state: `running`, `completed`, `failed`, `aborted`, `invalidated`, or `superseded`.
2. Run the provenance gate before analysis. Capture the exact command/launcher, resolved config snapshot, code revision and dirty state, environment/hardware, checkpoint lineage, dataset/split manifests or hashes, protocol version, seeds, timestamps, logs, metrics, predictions, and output paths.
3. Prefer machine-readable `config.json` and `provenance.json` beside the output. Preserve a human-readable critical-config summary in the experiment record and journal. Record explicit values rather than “default”; link the code revision that defines any unavoidable defaults.
4. If provenance is incomplete, recover fields only from contemporaneous artifacts. Mark unrecoverable fields `unknown / not recorded` with the reason. Never backfill a historical run using current script defaults.
5. Preserve the decisive key table with absolute values, baselines, sample count, aggregation, variability, and units.
6. Link full CSV/JSON/per-sample outputs; never hand-copy large raw arrays into prose.
7. Write observations before interpretations. Record alternative explanations and counterevidence.
8. Update `CURRENT.md` only if the authoritative present state changed.
9. Update `EXPERIMENTS.md` only according to the project's ownership policy. If human-owned, produce an exact proposed row or patch instead.

### `end`

Support experiment, implementation, diagnosis, planning, and literature-review sessions.

1. Inspect contemporaneous scripts, configs, logs, checkpoints, metrics, git state, and output directories before writing the handoff.
2. For experiment or evaluation sessions, apply the provenance gate from `record`. Add `## Key Configuration` and `## Artifact Index` to the journal. Keep the critical configuration readable; link the resolved full snapshot instead of pasting every field.
3. Write a concise journal/handoff containing work performed, evidence added, decisions made, files changed, running jobs, unresolved questions, and exact next actions.
4. Link experiment records rather than duplicating their full result tables.
5. Refresh `CURRENT.md` from authoritative records.
6. Promote only mature observations into `facts.md`; keep tentative explanations in hypotheses or experiment records.
7. Run `doctor` checks and report warnings without silently repairing scientific content.

An execution may be `completed` while reproducibility is `incomplete`. Do not mark evidence fully `valid/reproducible` when critical configuration is missing; report what is known and what cannot be recovered.

### `correct`

1. Freeze the affected record and mark its validity status.
2. State the invalidation scope: exact metrics, rows, claims, downstream documents, figures, and decisions affected.
3. Preserve the old values with a visible warning; do not delete them.
4. Create a corrected experiment/protocol version and link `supersedes` / `superseded_by` in both directions.
5. Recompute from source artifacts when possible. Do not merely edit headline numbers.
6. Audit downstream facts, CURRENT, tables, figures, and claims.
7. Record what remains valid after the correction.

### `synthesize`

Promote an item into durable knowledge only when its supporting evidence and protocol are traceable. Prefer scoped statements such as “under protocol P3 on split S2” over universal claims. Store unresolved mechanisms as hypotheses, not facts. Keep counterexamples and boundary conditions beside each promoted observation. Optionally run `jev_doctor.py` first to flag weakly supported or interpretation-laden observations, and verify every flagged item yourself before promoting.

### `claim-audit`

For every intended claim, build a claim-evidence matrix containing evidence IDs, protocol, comparison fairness, uncertainty, counterevidence, validity threats, and allowed wording. Classify each claim as `supported`, `partially-supported`, `unsupported`, or `invalidated`. Flag causal language without causal identification. Optionally pre-screen rows with `python3 scripts/jev_doctor.py <project-root>` (see *Optional Jev layers*) and manually review every low-confidence classification; the pre-screen is advisory, never the verdict.

### `doctor`

Keep this operation read-only. Run `python3 scripts/doctor.py <project-root>` from this skill directory when useful, then perform semantic checks that a script cannot reliably decide:

- current headline metrics disagree with experiment evidence;
- active claims depend on invalidated experiments;
- protocol changed without versioning;
- results omit N, baseline, aggregation, units, uncertainty, or artifact paths;
- completed/running experiments lack command, resolved config, code revision/dirty state, dataset split, seed, protocol, checkpoint lineage, logs, or metrics paths;
- a journal reports scientific results without `Key Configuration` and `Artifact Index`;
- interpretation is presented as evidence;
- a “best” result mixes splits, seeds, oracle alignment, or evaluation versions;
- CURRENT is stale or contains multiple competing current states;
- running work lacks resume information;
- important negative results or failure cases disappeared from synthesis.

Report severity as `critical`, `warning`, or `note`. Do not modify files in doctor mode.

When `TYPESAFE_API_KEY` is set, run `python3 scripts/jev_doctor.py <project-root>` after the structural audit for semantic pre-screening (see *Optional Jev layers*). Treat its findings as advisory: verify every warning yourself before acting on it, and personally review every item it lists for manual review. Without the key, skip it and perform the semantic checks yourself as above.

## Optional Jev layers

Two optional layers are backed by TypeSafe Jev, a non-generative "System One" decision model. Both are opt-in: without `TYPESAFE_API_KEY` in the environment the scripts print a skip/fallback note and exit 0, and every workflow above works unchanged offline — the agent simply performs these judgments itself (the semantic checks inside `doctor`/`claim-audit`/`synthesize`, and the fixed `start` reading order). Treat the Jev layers as a faster, cheaper executor for judgments the agent can already make; they are never a capability gate.

**Context triage (`start`, every session).** `python3 scripts/jev_context.py <project-root> --task "<request>"` ranks candidate memory items (experiment records, knowledge entries, protocols, journals) against the task in one batched call and prints a manifest under a character budget: `ALWAYS` (operational entry + CURRENT.md, never triaged), `LOAD` (read in full), `SKIP` (pointers only), `SURFACE` (validity warnings, printed even for skipped items), `SUMMARY`. Read what it marks `LOAD`; keep `SKIP` as one-line pointers. Relevance never hides a staleness alarm: relay every `SURFACE` line. On `FALLBACK` (no key, API failure), follow the fixed reading order unchanged.

**Semantic doctor (`doctor`, `claim-audit`, `synthesize`; occasional).** `python3 scripts/jev_doctor.py <project-root>` pre-screens experiment records (provenance recoverable, headline matches the table, observations free of interpretation), CURRENT consistency, and claim support against the controlled vocabulary. Funnel: `doctor.py` (local regex, free) → `jev_doctor.py` (batched semantic triage) → your own review of the low-confidence items (the only authority).

Shared rules:

- Jev findings are advisory triage, never verdicts. Do not edit scientific content, and never drop a `SURFACE` warning, because of a Jev result; verify first.
- Both scripts are read-only and never write files.
- Below the confidence threshold (default 0.5; `--min-confidence` on `jev_doctor.py`), findings become manual-review items instead of warnings.
- Calibrate before trusting: for the first weeks, compare Jev output against your own decisions and tune thresholds per project; scientific use should err toward more review.
- `--dry-run` on either script prints inventory and request previews without calling the API.
- `jev_doctor.py` always exits 0 (triage, not a gate); `doctor.py` remains the exit-code authority for CI.

## Status and validity vocabulary

Use controlled terms consistently:

- Experiment execution: `proposed`, `ready`, `running`, `completed`, `failed`, `aborted`.
- Evidence validity: `unchecked`, `valid`, `suspect`, `invalidated`, `superseded`.
- Interpretation maturity: `hypothesis`, `tentative`, `supported`, `refuted`.
- Claim support: `supported`, `partially-supported`, `unsupported`, `invalidated`.

“Completed” does not mean “valid”; a completed run may later be invalidated.

## Safe editing policy

- When adopting into a project that already has documentation, preserve its structure unless the user explicitly requests replacement.
- Prefer small patches and links over copying the same truth into several files.
- Before changing a current headline result, cite the evidence record that authorizes the change.
- When evidence conflicts, surface the conflict and keep both records until resolved.
- Never fabricate provenance, seeds, sample counts, paths, or metric values.
- Never reconstruct an old run from the current version's defaults; use only contemporaneous artifacts and mark the rest unknown.
- Keep `doctor` and default `start` read-only.
