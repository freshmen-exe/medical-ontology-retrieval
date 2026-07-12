# Source and Citation Policy

## 1. Purpose

Every external fact, dataset, algorithm reference, model, tool, and competition clarification must remain traceable. Links should not exist only in chat history.

## 2. Source locations

| Source type | Repository path |
|---|---|
| Original competition PDF/Markdown | `docs/problem_statement/original/` |
| Team interpretation of the task | `docs/problem_statement/derived/` |
| Competition announcements/clarifications | `references/competition/` |
| Public source registry | `references/source_registry.md` and `.jsonl` |
| BibTeX references | `references/report_references.bib` |
| Raw dataset provenance | `data/raw/<dataset>/SOURCE.md` |
| Algorithm reading notes | `references/algorithms.md` |
| Tool documentation links | `references/tooling.md` |
| Data-source links | `references/data_sources.md` |

## 3. Required registry fields

Each source entry records:

```text
ID / citation key
Title
Publisher or organization
URL
Source type
Authority level
Access date
Version or publication date
Used for
License or access restrictions
Local file path if downloaded
Checksum if applicable
Notes
```

## 4. Authority levels

1. Organizer-provided material.
2. Government/standards-body/official product documentation.
3. Peer-reviewed paper or official research repository.
4. Reputable technical reference.
5. Community source used only for troubleshooting or discovery.

Lower-authority sources never override organizer or official sources.

## 5. Vietnamese ICD-10 rule

The target is the Vietnamese ICD-10 list associated with Circular 06/2026/TT-BYT. Do not silently substitute ICD-10-CM or a generic WHO export.

Primary sources:

- Government document page.
- Circular PDF.
- Official appendix PDF.
- `icd.kcb.vn` for lookup and cross-checking.

## 6. RxNorm rule

Use an official 2026 NLM RxNorm monthly release. Record the exact monthly release date and file checksum. A UMLS Terminology Services account/license may be required.

## 7. Raw data policy

Do not commit full raw licensed data. Commit:

- `SOURCE.md`
- download/parse scripts
- checksum manifests
- schemas
- tiny synthetic or permitted fixtures

Use the team's shared artifact storage for large source archives and indexes. Record the location and checksum in `artifacts/README.md` or the dataset `SOURCE.md`.

## 8. Report citation workflow

1. Register the source.
2. Add or update its BibTeX entry.
3. Cite it in LaTeX by citation key.
4. Verify title, author/publisher, year, and URL.
5. Avoid citing a mirror when an authoritative source is available.

## 9. Link maintenance

QA verifies critical source links before report freeze. If a URL changes, keep the old access date and add the replacement URL rather than deleting provenance.
