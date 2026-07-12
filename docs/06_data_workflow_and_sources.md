# Data and Ontology Workflow

## 1. Target systems

```text
CHẨN_ĐOÁN → Vietnamese ICD-10 under Circular 06/2026/TT-BYT
THUỐC     → official NLM RxNorm 2026 RXCUI
```

Do not use ICD-10-CM as the diagnosis target. Do not use ATC, NDC, SNOMED CT, MeSH, or UMLS CUI as final drug/diagnosis candidates unless the organizer changes the requirement.

## 2. Source hierarchy

### Vietnamese ICD-10

1. Organizer-provided source if one is later released.
2. Government Circular 06/2026/TT-BYT and its official appendix.
3. `icd.kcb.vn` for lookup and cross-checking.
4. Mirrors only as parsing aids, never as authority.

### RxNorm 2026

1. Official NLM monthly release archive.
2. Official NLM release notes and file documentation.
3. RxNorm/RxNav APIs for spot verification.

## 3. Raw-source handling

Raw folders:

```text
data/raw/icd10_vi_2026/
data/raw/rxnorm_2026/
```

Each source folder must contain `SOURCE.md` with:

- title and publisher;
- exact URL;
- access date;
- release/version date;
- local filename;
- SHA-256 checksum;
- license/access restrictions;
- parser script and parser commit;
- known issues.

Never edit source files in place. Parser corrections happen in code, not by silently changing the raw archive/PDF.

## 4. Processing stages

```text
raw source
→ parser-specific intermediate rows
→ normalized canonical records
→ scope selection
→ alias generation
→ alias collision/quality validation
→ processed JSONL
```

Use `data/interim/` for parser output that is not yet trusted. Use `data/processed/` only for schema-validated data.

## 5. Canonical ICD record

Required fields:

```json
{
  "code": "K21.9",
  "code_no_dot": "K219",
  "name_vi": "...",
  "name_en": "...",
  "chapter_code": "K00-K93",
  "chapter_name_vi": "...",
  "block_code": "...",
  "block_name_vi": "...",
  "source_version": "TT06/2026/TT-BYT",
  "source_row": "..."
}
```

Preserve meaningful symbols, dagger/asterisk information, exclusions, sex/age restrictions, or usage notes when the official source provides them. Do not flatten information that may help candidate validation.

## 6. Canonical RxNorm record

Required fields:

```json
{
  "rxcui": "1191",
  "name": "Aspirin",
  "tty": "IN",
  "sab": "RXNORM",
  "suppress": "N",
  "source_version": "RxNorm 2026-07-06"
}
```

Initial TTY scope:

```text
IN   ingredient
PIN  precise ingredient
MIN  multiple ingredients
SCD  semantic clinical drug
SBD  semantic branded drug
BN   brand name
```

Package concepts are optional and require an explicit mapping need.

## 7. Scope selection

Do not choose records manually one by one. Build a reproducible filter and priority score using:

- diagnosis/drug categories relevant to the task examples and clinical notes;
- active/non-suppressed concepts;
- common internal-medicine coverage;
- presence of usable official names and aliases;
- concepts represented in QA cases and error analysis;
- memory/build constraints.

Record the inclusion criteria and counts in `data/processed/README.md`. Do not hide cherry-picked inclusions.

## 8. Alias generation

Mechanical alias generation is code, not LLM generation.

Safe operations include:

- Unicode/whitespace normalization;
- lowercase representation for matching;
- punctuation and hyphen spacing variants;
- Vietnamese accentless matching representation;
- verified unit spacing variants such as `500 mg`/`500mg`;
- official RxNorm source strings that map to the same RXCUI;
- reviewed abbreviations.

Unsafe operations include:

- removing clinically distinguishing qualifiers;
- mapping symptoms to a diagnosis;
- mapping an ingredient-only name to a dosage-specific SCD;
- merging aliases with different RXCUIs/codes;
- using LLM suggestions without review.

Each alias record includes provenance and quality:

```json
{
  "alias": "GERD",
  "normalized_alias": "gerd",
  "code": "K21.9",
  "canonical_name": "...",
  "system": "ICD10_VI",
  "language": "en",
  "alias_type": "abbreviation",
  "quality": "high",
  "source": "reviewed_abbreviation",
  "source_version": "TT06/2026/TT-BYT"
}
```

Quality values:

- `high`: official or verified equivalent.
- `medium`: deterministic variant preserving meaning.
- `weak`: ambiguous or unverified; excluded from default indexes.

## 9. Collision validation

The validator must report:

- identical normalized alias mapped to multiple codes;
- duplicate alias/code rows;
- missing canonical code/name;
- wrong system or version;
- suspiciously short aliases;
- alias equal to a generic symptom/result term;
- dosage/form information lost across RxNorm TTY levels.

Collisions are reviewed; they are not silently resolved by taking the first row.

## 10. Processed outputs

```text
data/processed/icd10_vi_codes_core.jsonl
data/processed/rxnorm_2026_codes_core.jsonl
data/processed/icd10_vi_aliases_core.jsonl
data/processed/rxnorm_2026_aliases_core.jsonl
data/processed/abbreviations.jsonl
data/candidates/weak_aliases.jsonl
data/processed/data_manifest.json
```

The manifest contains record counts, source versions, script commits, timestamps, and checksums.

## 11. Data role after index handoff

Data work continues after vector indexes exist:

- answer parser/ontology questions;
- maintain provenance;
- review retrieval failures caused by missing/noisy aliases;
- update aliases through reviewed PRs;
- support QA in expected-code verification;
- freeze data versions for experiments and report tables.
