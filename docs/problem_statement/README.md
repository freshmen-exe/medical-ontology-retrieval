# Problem Statement Archive

This directory stores the official contest/task statement and team-derived notes.

## What goes here

```text
docs/problem_statement/
├── original/
│   ├── Viettel_AI_Race_2026_Bai_2.pdf        # Official PDF or downloaded task statement
│   ├── Viettel_AI_Race_2026_Bai_2.md         # Markdown transcription or notes, if created
│   └── SOURCE.md                             # Where the statement came from
└── derived/
    ├── task_summary.md                       # Team-readable task summary
    ├── output_schema.md                      # Required JSON output schema
    ├── evaluation_metrics.md                 # Scoring formula and metric notes
    └── assumptions.md                        # Assumptions confirmed by organizers or the team
```

## Rules

- Do not edit files in `original/` after saving them.
- If the official PDF changes, add a new dated copy instead of overwriting the old one.
- Put interpretations and summaries in `derived/`, not in `original/`.
- Any claim used in the report should also be logged in `references/source_registry.md` or `references/source_registry.jsonl`.
