# Evidence-grounded manuscript context

## Contents

1. Purpose and authority
2. Manuscript workspace
3. Paper-start workflow
4. Context contracts
5. Migration and release rules

## 1. Purpose and authority

A manuscript workspace is a writing and submission projection over canonical project evidence. It helps an agent recover the paper's argument, allowed numbers, limitations, and artifact lineage without loading the full project history.

Keep the authority direction one-way:

```text
protocols + experiment records + raw artifacts
                    -> manuscript context
                    -> LaTeX, figures, tables, supplement
                    -> immutable release
```

Never use manuscript prose or a copied table to overwrite experiment history. A recent draft is not evidence. A paper context may lag canonical evidence; `paper-start` must detect and report that lag.

## 2. Manuscript workspace

Prefer `manuscripts/<paper-id>/` when a project can produce multiple papers. Adapt an equivalent existing location instead of creating competing active manuscripts.

```text
manuscripts/<paper-id>/
├── MANUSCRIPT.md
├── manuscript.yaml
├── src/                       # authoritative LaTeX source after migration
├── bibliography/
├── figures/
│   ├── source/
│   ├── final/
│   └── manifest.yaml
├── tables/
│   ├── data/
│   ├── generated/
│   └── manifest.yaml
├── supplement/
├── context/
│   ├── paper-state.md
│   ├── claim-evidence.md
│   ├── number-registry.yaml
│   ├── limitations.md
│   ├── protocol-map.md
│   └── artifact-index.json
├── reviews/
├── scripts/
├── build/                     # generated, normally ignored
└── dist/                      # generated releases
```

Do not copy checkpoints, large prediction arrays, experiment logs, or raw datasets into the manuscript workspace. Link their canonical paths and hashes.

During staged migration, declare the existing LaTeX entry in `manuscript.yaml` and mark the new `src/` state explicitly. Do not create two apparently authoritative editable copies.

## 3. Paper-start workflow

1. Resolve the target manuscript. If several exist and no target is given, list them and use an explicitly declared default only when present.
2. Read `manuscript.yaml`; verify every authority and source path exists.
3. Read `paper-state.md` as navigation, not scientific truth.
4. Map intended claims to project claim IDs and experiment IDs.
5. Verify every headline entry in `number-registry.yaml` against its experiment record, protocol, split, N, aggregation, uncertainty, units, validity, and raw artifact.
6. Search current warnings for invalidated/superseded evidence and trace their downstream manuscript impact.
7. Inspect figure and table manifests. Flag assets without evidence IDs, generation sources, or status.
8. Inspect only the manuscript sections and latest reviews needed for the request.

Report:

- current paper thesis and contribution boundaries;
- safe, conditional, unsupported, and invalidated claims;
- authoritative numbers and their evidence paths;
- stale or conflicting manuscript numbers;
- figures, tables, captions, abstract, or sections affected by corrections;
- evidence gaps versus writing-only gaps;
- exact already-decided next writing action and optional suggestions.

## 4. Context contracts

### `manuscript.yaml`

Record the paper ID, status, target, authoritative language, current LaTeX entry, context files, project authority paths, build method, and migration state. Unknown venue or metadata remains `null`.

### `paper-state.md`

Keep the current thesis, contribution list, active writing stage, authoritative source entry, completed sections, blockers, and next actions. Do not duplicate experiment tables.

### `claim-evidence.md`

Project the canonical claim registry into the paper's intended wording. Include evidence, counterevidence, scope, support status, allowed wording, and manuscript locations. A project claim may exist without appearing in this paper.

### `number-registry.yaml`

Register each headline number with a stable key and at least:

- experiment ID and evidence path;
- protocol;
- model/variant, split, N, seeds, aggregation, units;
- exact value and uncertainty when available;
- raw artifact path;
- validity and manuscript-authority status;
- supersedes/superseded-by relation when applicable.

Use `unknown`, `not measured`, or `not applicable` rather than inventing fields. A corrected result pending required review may be valid evidence but not yet manuscript authority; encode both states.

### Figure and table manifests

For every manuscript asset, record its final file, source or generation command, evidence IDs, protocols, claim IDs, caption scope, and status. Tables should be generated from registered data where practical; avoid hand-copying headline values into multiple files.

### `limitations.md`

Preserve negative results, counterexamples, generalization boundaries, fairness limits, protocol deviations, and wording constraints that must survive prose polishing.

## 5. Migration and release rules

Adopt a manuscript workspace additively. First inventory the existing active source, declare it in `manuscript.yaml`, and establish context/manifests. Move the LaTeX source only in a separate verified migration that leaves one active authority and a clear legacy pointer.

A release should contain compiled manuscript and supplement PDFs, the submission source package, bibliography form required by the venue, and a machine-readable release manifest with code revision, dirty state, evidence-context hashes, build command, timestamp, and included files.

Before freezing a release, check unresolved citations/references, missing assets, bilingual synchronization when applicable, unregistered headline numbers, invalidated evidence dependencies, stale figure/table manifests, and divergence between the release source and the declared manuscript entry.
