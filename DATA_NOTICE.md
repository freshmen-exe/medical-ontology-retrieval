# Data, Model, and Competition Material Notice

The MIT license applies only to team-authored source code and documentation where the team has the
right to license it. It does not relicense:

- Vietnamese ICD-10 source documents;
- RxNorm/UMLS files;
- competition statements, test data, or organizer material;
- Ollama model weights;
- third-party papers, figures, or datasets.

## Repository policy

Commit provenance and reproducibility material:

- official URLs;
- exact release/version identifiers;
- access dates;
- SHA-256 checksums;
- parser scripts;
- schemas;
- small lawful fixtures;
- record counts and validation reports.

Do not commit full raw archives, model weights, generated embedding matrices, HNSW pickles, private
clinical data, access tokens, or restricted competition files unless redistribution has been
explicitly confirmed.

Every external source used in implementation or reporting must be registered in
`references/source_registry.md` and, for downloaded data, in the corresponding
`data/raw/.../SOURCE.md`.
