# Evidence-first research lifecycle

## Contents

1. Frame the problem
2. Map prior knowledge
3. Design the study
4. Register and execute
5. Validate measurements
6. Analyze without overclaiming
7. Correct and supersede
8. Synthesize knowledge
9. Build claims
10. Reproduce, transfer, and archive

## 1. Frame the problem

Define the research question before selecting the method. Record the unit of analysis, population/domain, intended contribution, constraints, primary outcome, and what would count as failure. Separate engineering targets from scientific claims.

## 2. Map prior knowledge

Keep literature notes separate from project evidence. Record citation, exact claim, experimental setting, comparability limits, and how it affects a project hypothesis. Never import a paper's metric as a baseline unless dataset, split, preprocessing, and evaluation are comparable.

## 3. Design the study

Prefer experiments that distinguish competing explanations. Specify:

- baseline and controls;
- independent/dependent variables;
- confounders and leakage paths;
- primary metric chosen before results;
- sample size, seeds, uncertainty, and subgroup analysis;
- acceptance and falsification conditions;
- compute budget and stop rules;
- sanity checks and expected failure signatures.

Label exploratory experiments. Do not retrofit confirmatory language after seeing their results.

## 4. Register and execute

Create a stable experiment ID before or at launch. Record the exact command, code revision, config, environment, data lists, protocol version, seeds, logs, checkpoints, and scheduler IDs. While running, store enough information for another session to monitor or resume without guessing.

Execution failure is evidence about the pipeline, not evidence for or against the scientific hypothesis unless the measurement remains valid.

## 5. Validate measurements

Before interpreting headline metrics, verify:

- input/GT units and ranges;
- masks, resize, normalization, alignment, and aggregation;
- train/validation/test overlap;
- sample counts and missing outputs;
- baseline reproduction;
- per-sample distributions and obvious outliers;
- invariant or synthetic fixtures with known answers;
- raw predictions against a few visual examples when appropriate.

Treat validation as part of the experiment, not post-hoc housekeeping.

## 6. Analyze without overclaiming

Write the decisive table first. Then record:

1. Observation: what the table directly shows.
2. Interpretation: a possible explanation.
3. Alternatives: other explanations consistent with the data.
4. Counterevidence: results that weaken the preferred explanation.
5. Decision: what to do next and why.

Report absolute baseline and treatment values, not only percentage improvement. Preserve N, variability, units, split, protocol, and whether alignment is raw or oracle. Avoid selecting only favorable metrics or scenes.

## 7. Correct and supersede

When a bug or protocol flaw is found, build an impact graph:

```text
bug/protocol flaw
  -> affected artifacts
  -> affected metrics/tables
  -> affected observations/facts
  -> affected decisions
  -> affected figures/claims/reports
```

Keep the invalid record visible with a warning. Recompute from source artifacts, assign a corrected ID or protocol version, and link replacements bidirectionally. State which unaffected evidence remains trustworthy.

## 8. Synthesize knowledge

Promote only traceable, scoped observations. A result from one split and seed should not become a universal fact. Keep mechanisms in the hypothesis registry until discriminating evidence exists. Periodically consolidate duplicate observations while retaining source links.

## 9. Build claims

Construct the claim-evidence matrix. For each claim, check:

- comparison fairness;
- statistical and practical significance;
- generalization domain;
- causal identification;
- negative evidence and limitations;
- reproducibility path from headline number to raw artifact.

Use wording strength that matches support. “Outperforms” requires a comparable baseline; “causes” requires causal evidence; “generalizes” requires held-out domains appropriate to that claim.

## 10. Reproduce, transfer, and archive

Before a milestone or handoff, verify that a fresh session can locate the code revision, environment, data manifest, configs, checkpoints, commands, raw outputs, evaluation scripts, and expected key values. Archive immutable artifacts or hashes where storage permits. Keep CURRENT focused on active work and move retired detail out of the resume path without deleting history.

