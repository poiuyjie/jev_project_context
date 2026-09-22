# Project Context V2

**English** | [简体中文](README.zh-CN.md)

Evidence-first, long-term experiment memory for AI coding agents. Every claim stays traceable from question to evidence, every session resumable without archaeology.

Research projects rarely die because results are lost — they die because their *context* is: which config produced that number, why this baseline, what was invalidated, what was merely hypothesized. This skill turns an AI agent (Claude Code, ZCode, any skills-compatible agent) into a disciplined lab-notebook keeper: 10 operations, a controlled validity vocabulary, provenance gates, and read-only audits.

## How it works

```mermaid
flowchart TB
    init(["init — adopt once"]) --> frame

    subgraph cycle ["Research loop"]
        direction LR
        frame["frame — question, hypotheses, falsifiers"]
        plan["plan — stable experiment ID, frozen protocol"]
        record["record — provenance gate, evidence before interpretation"]
        close["End — journal handoff, refresh CURRENT"]
        frame --> plan --> record --> close
    end

    close --> start(["start — resume next session"])
    start --> frame
    close --> synthesize["synthesize — promote traceable observations to facts"]
    close -.-> correct["correct — freeze, invalidate, supersede"]
    correct -.-> record
    close ==> doctor["doctor — structural + optional semantic audit"]

    classDef gate fill:#e8f0fe,stroke:#4285f4,color:#174ea6;
    classDef write fill:#fef7e0,stroke:#f9ab00,color:#7d5600;
    classDef read fill:#e6f4ea,stroke:#34a853,color:#0d652d;
    class init,frame,plan,record,close write;
    class start,synthesize read;
    class correct,doctor gate;
```

### The audit funnel and context triage

`doctor` audits in layers, and `start` loads only what the task needs. Both optional Jev layers degrade gracefully to fully offline behavior when `TYPESAFE_API_KEY` is unset.

```mermaid
flowchart LR
    subgraph audit ["doctor · audit funnel"]
        direction TB
        L1["doctor.py — local regex, free, exit code for CI"] --> L2["jev_doctor.py — semantic pre-screen (optional)"]
        L2 -->|"low confidence"| L3["Agent / human review — the only authority"]
        L2 -->|"high-confidence warning"| L3
    end

    subgraph ctx ["start · context triage (every session)"]
        direction TB
        S1["jev_context.py — rank memory items against the task"] --> S2["manifest: ALWAYS / LOAD / SKIP / SURFACE"]
        S2 --> S3["agent reads LOAD only; SURFACE warnings always relayed"]
    end

    classDef layer fill:#e8f0fe,stroke:#4285f4,color:#174ea6;
    classDef brain fill:#fce8e6,stroke:#ea4335,color:#a50e0e;
    class L1,L2,S1,S2,S3 layer;
    class L3 brain;
```

## Operations

| Operation | Purpose | Mutation |
|---|---|---|
| `init` | Initialize the memory structure (missing files only) | write |
| `start` | Resume: task-conditioned context load + state report | read-only |
| `frame` | Research question, hypotheses, falsifiers, confounders | write (confirmed) |
| `plan` | Register experiment: ID, frozen protocol, acceptance criteria | write |
| `record` | Evidence + provenance gate + key tables | write |
| `end` | Journal handoff, refresh CURRENT, run doctor | write |
| `correct` | Freeze old record, scope the invalidation, link replacement | write |
| `synthesize` | Promote traceable observations into durable facts | write |
| `claim-audit` | Claim–evidence matrix with support classification | read-only |
| `doctor` | Structural + optional semantic health audit | read-only |

## Install

Requires Python ≥ 3.10 for the scripts (zero third-party dependencies).

```bash
# via the skills CLI (project-level; add -g for global)
npx skills add poiuyjie/jev_project_context

# or copy the folder into your agent's skills directory
git clone https://github.com/poiuyjie/jev_project_context ~/.agents/skills/project-context-v2
```

Then, inside your research project, tell your agent:

> initialize research memory for this project

Daily use: *"continue this project"* (start), *"record the results of E2026-0922-01"* (record), *"close the session"* (end).

### Optional Jev layers

Two scripts become active when `TYPESAFE_API_KEY` is set (get a key at [console.typesafe.ai](https://console.typesafe.ai/keys); see [TypeSafe/Jev docs](https://docs.typesafe.ai)):

- `jev_context.py` — task-conditioned context triage for `start`: ranks experiment records, knowledge entries, protocols, and journals against the current task in one batched decision call, and prints a `LOAD / SKIP` manifest under a character budget. Relevance never hides staleness: `SURFACE` validity warnings (invalidated/superseded evidence) are printed even for skipped items.
- `jev_doctor.py` — semantic pre-screening for `doctor` / `claim-audit` / `synthesize`: provenance recoverability, headline-vs-table consistency, interpretation leaking into observations, and claim-support classification over the controlled vocabulary.

Both are read-only and advisory: findings are triage, never verdicts. Without the key (or on API failure) they print a fallback note and exit 0 — every workflow works fully offline.

## Memory layout

```text
project/
├── AGENTS.md / CLAUDE.md    # operational entry
├── CURRENT.md               # authoritative present-state projection
├── EXPERIMENTS.md           # compact registry and decisive tables
└── docs/
    ├── protocols/           # versioned evaluation protocols
    ├── research/            # questions, hypotheses, claims
    ├── knowledge/           # facts, bugs, decisions, patterns
    ├── experiments/         # one evidence record per experiment ID
    └── journal/             # session handoffs
```

Schemas for every file: [references/schemas.md](references/schemas.md).

## Core principles

1. **Evidence outlives interpretation.** Observations are recorded before interpretations; a correction replaces the analysis, never the record.
2. **Completed ≠ valid.** Execution state and evidence validity are separate axes; runs start `unchecked`.
3. **Provenance before analysis.** Command, resolved config, code revision, split, seed, protocol — unrecoverable fields are marked `unknown`, never backfilled from current defaults.
4. **Never rewrite history silently.** Invalidated results stay visible with warnings and bidirectional `supersedes/superseded_by` links.
5. **Audits are read-only.** `doctor` and `start` never mutate; Jev findings are advisory only.

## License

[MIT](LICENSE)
