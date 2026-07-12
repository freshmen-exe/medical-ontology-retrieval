# Output Schema Interpretation

The executable schema is stored in:

- `schemas/entity.schema.json`
- `schemas/output.schema.json`

Conceptual entity shape:

```json
{
  "text": "exact substring",
  "position": [0, 10],
  "type": "CHẨN_ĐOÁN",
  "assertions": {
    "isNegated": false,
    "isFamily": false,
    "isHistorical": false
  },
  "candidates": ["K21.9"]
}
```

Rules:

1. `position` uses the project convention `[start, end)` and must satisfy
   `raw_text[start:end] == text`.
2. `assertions` is present only for symptoms, diagnoses, and drugs.
3. `candidates` is present only for diagnoses and drugs.
4. Diagnosis codes come from the Vietnamese ICD-10 target; drug codes are RxNorm 2026 RXCUIs.
5. Candidate codes are unique and ranked best first.
6. No entity or code may be invented outside the input/loaded ontology.

Before final submission, compare this derived interpretation with the original organizer file and
record any discrepancy in `references/competition/clarifications.md`.
