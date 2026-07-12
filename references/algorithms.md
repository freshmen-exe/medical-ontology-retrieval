# Algorithm Reading Map

Read only the section needed for the current Jira task; do not delay implementation by reading
every source first.

## Exact cosine search

- Stanford IR Book — vector space scoring and cosine similarity:
  https://nlp.stanford.edu/IR-book/
- Project contract: `docs/13_api_spec.md`.
- Implementation: `src/medical_ontology/retrieval/exact_search.py`.

## BM25 and character TF-IDF

- Okapi BM25 background:
  https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html
- Implementation: `retrieval/bm25.py` and `retrieval/tfidf.py`.
- Required experiments: token BM25, character TF-IDF, and combined RRF.

## Reciprocal Rank Fusion

- Primary paper: https://doi.org/10.1145/1571941.1572114
- Project rule: collapse aliases to the best alias per code before fusion.
- Implementation: `retrieval/rrf.py` and `mapping/candidate_ranker.py`.

## HNSW

- Primary paper: https://arxiv.org/abs/1603.09320
- Required invariants: randomized levels, hierarchical greedy descent, layer-zero candidate
  search, bidirectional edges, degree limits, neighbor pruning, `ef_construction`, and `ef_search`.
- Implementation: `retrieval/hnsw.py`.
- Benchmark: exact-search Recall@k and latency; HNSW is not accepted merely because it runs.
