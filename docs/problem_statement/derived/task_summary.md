# Task Summary

The system reads free-form clinical text and returns medical entities with exact source spans,
required labels, assertion attributes, and ontology candidates.

## Required entity labels

- `TRIỆU_CHỨNG`
- `TÊN_XÉT_NGHIỆM`
- `KẾT_QUẢ_XÉT_NGHIỆM`
- `CHẨN_ĐOÁN`
- `THUỐC`

Assertions apply to symptoms, diagnoses, and drugs:

- `isNegated`
- `isFamily`
- `isHistorical`

Candidates apply only to:

- `CHẨN_ĐOÁN` → Vietnamese ICD-10 target confirmed by the organizer;
- `THUỐC` → RxNorm 2026 RXCUI.

The output `text` and `position` must refer to the exact original note. Internal canonical names or
abbreviation expansions must never replace the raw span.

The competition test package contains numbered text files, and the submission package contains
corresponding numbered JSON files under an `output/` directory. Verify the exact count and packaging
rules against the untouched PDF before submission.
