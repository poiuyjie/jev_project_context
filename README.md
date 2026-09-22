# Project Context V2

**English** | [简体中文](README.zh-CN.md)

Evidence-first, long-term experiment memory for AI coding agents. Every claim stays traceable from question to evidence, every session resumable without archaeology.

Research projects rarely die because results are lost — they die because their *context* is: which config produced that number, why this baseline, what was invalidated, what was merely hypothesized. This skill turns an AI agent (Claude Code, ZCode, any skills-compatible agent) into a disciplined lab-notebook keeper: 10 operations, a controlled validity vocabulary, provenance gates, and read-only audits.

## How it works

```mermaid
flowchart TB
    %%{init: {"flowchart":{"defaultRenderer":"elk"},"theme":"base","themeVariables":{"fontFamily":"Inter, ui-sans-serif, system-ui, sans-serif","fontSize":"14px","clusterBkg":"#F8FAFC","clusterBorder":"#CBD5E1","lineColor":"#94A3B8","edgeLabelBackground":"#FFFFFF"}}}%%

    init(["✦ init — adopt once"]):::seed --> startS

    subgraph loop["🔬 Per-session loop"]
        startS(["▶ start — load task-conditioned context"]):::seed
        frame["🎯 frame<br/>question · hypotheses · falsifiers"]:::op
        plan["📋 plan<br/>stable experiment ID · frozen protocol"]:::op
        record["🧾 record<br/>provenance gate · evidence before interpretation"]:::op
        endS(["🏁 End — journal handoff"]):::op
        startS --> frame --> plan --> record --> endS
        endS -. next session .-> startS
    end

    endS --> syn["📦 synthesize<br/>promote traceable observations to facts"]:::read

    subgraph guards["⚠️ Available anytime"]
        correct["🧊 correct<br/>freeze · invalidate · supersede"]:::gate
        doctor["🩺 doctor<br/>read-only structural + semantic audit"]:::gate
    end

    endS -. bug found .-> correct
    endS == close-out ==> doctor

    classDef seed fill:#EEF2FF,stroke:#6366F1,stroke-width:2px,color:#312E81;
    classDef op fill:#FFFFFF,stroke:#6366F1,stroke-width:1.5px,color:#1E1B4B;
    classDef read fill:#ECFDF5,stroke:#10B981,stroke-width:1.5px,color:#064E3B;
    classDef gate fill:#FFF7ED,stroke:#F59E0B,stroke-width:1.5px,color:#7C2D12;
```

### The audit funnel and context triage

`doctor` audits in layers, and `start` loads only what the task needs. Both optional Jev layers degrade gracefully to fully offline behavior when `TYPESAFE_API_KEY` is unset.

```mermaid
flowchart TB
    %%{init: {"flowchart":{"defaultRenderer":"elk"},"theme":"base","themeVariables":{"fontFamily":"Inter, ui-sans-serif, system-ui, sans-serif","fontSize":"14px","clusterBkg":"#F8FAFC","clusterBorder":"#CBD5E1","lineColor":"#94A3B8","edgeLabelBackground":"#FFFFFF"}}}%%
    subgraph audit["🩺 doctor — audit funnel"]
        direction LR
        l1["doctor.py<br/>local regex · free · CI exit code"]:::c1
        l2["jev_doctor.py<br/>semantic pre-screen · optional Jev"]:::c2
        l3(["🧠 agent / human review<br/>the only authority"]):::c3
        l1 -->|structural findings| l2
        l2 -->|flagged findings| l3
    end

    subgraph triage["🧭 start — context triage · every session"]
        direction LR
        s1["memory cards<br/>experiments · facts · protocols · journals"]:::c1
        s2["jev_context.py<br/>task-conditioned relevance scoring"]:::c2
        s3(["LOAD / SKIP manifest<br/>SURFACE warnings always relayed"]):::c3
        s1 --> s2 --> s3
    end

    audit ~~~ triage

    classDef c1 fill:#EEF2FF,stroke:#6366F1,stroke-width:1.5px,color:#312E81;
    classDef c2 fill:#FFFFFF,stroke:#6366F1,stroke-width:1.5px,color:#1E1B4B;
    classDef c3 fill:#FFF1F2,stroke:#F43F5E,stroke-width:2px,color:#881337;
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

Two scripts become active once `TYPESAFE_API_KEY` is configured. The simplest way is a `.env` file:

```bash
cp .env.example .env   # then paste your key from https://console.typesafe.ai/keys
```

`jev_client.py` loads `.env` from the current directory, the `scripts/` directory, or the skill root — no dependencies, and real environment variables always take precedence. `.env` is git-ignored: never commit a real key.

With the key in place (see [TypeSafe/Jev docs](https://docs.typesafe.ai)):

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
