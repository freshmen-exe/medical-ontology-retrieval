# Report, Slides, and Demo Video

## 1. Storage structure

```text
reports/
├── drafts/
├── final/
└── latex/
    ├── main.tex
    ├── sections/
    ├── figures/
    ├── tables/
    └── references.bib

slides/
├── outline.md
├── figures/
├── pptx/
└── exports/

videos/
├── script.md
├── demo_checklist.md
├── raw/
├── edited/
└── final/
```

## 2. Source rule

Before citing a public source:

1. register it in `references/source_registry.md`/`.jsonl`;
2. add a BibTeX entry;
3. store downloaded public documents only when licensing permits;
4. cite the authoritative source rather than a mirror.

## 3. LaTeX report structure

Recommended sections already exist under `reports/latex/sections/`:

1. Introduction and motivation.
2. Task definition and scoring.
3. Vietnamese ICD-10 and RxNorm 2026 data workflow.
4. Entity/assertion extraction.
5. Dense, sparse, RRF, and HNSW methodology.
6. Pipeline and validation.
7. Evaluation setup.
8. Results and ablation.
9. Error analysis and limitations.
10. Conclusion and team contribution.

Report claims must match committed results and configuration. Do not report unrepeatable best runs without context.

## 4. Figures and tables

Generated figures/tables should have a source script or documented generation procedure. Use stable filenames. Store editable source separately from exported images when applicable.

Examples:

```text
experiments/retrieval_results.csv
reports/latex/tables/retrieval_results.tex
reports/latex/figures/system_architecture.pdf
slides/figures/system_architecture.png
```

## 5. Slides

Keep one clear message per slide. Suggested order:

1. Problem and required outputs.
2. Constraints and self-implementation policy.
3. Data sources.
4. End-to-end architecture.
5. Extraction method.
6. Hybrid retrieval and RRF.
7. HNSW implementation.
8. Validation and QA.
9. Results/ablation.
10. Demo and limitations.
11. Team contributions.

## 6. Video

The video script and shot checklist are version-controlled. Record only after the release candidate demo is stable.

Demo sequence:

1. State the problem.
2. Show architecture briefly.
3. Start or show model/index status.
4. Run a fixed clinical example.
5. Show entities, assertions, candidates, and final JSON.
6. Show one hard case/error-handling example.
7. Show metrics.
8. State limitations honestly.

Never display secrets, private notes, local personal paths, or restricted raw data.

## 7. Review gates

- Technical accuracy: Model/Pipeline owners.
- Data/source/citation accuracy: Data owner.
- Metric accuracy and reproducibility: QA.
- Final narrative and timing: Tech Lead.
