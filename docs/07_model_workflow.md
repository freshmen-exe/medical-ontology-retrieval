# Model and Retrieval Workflow

The Model role owns extraction behavior and retrieval/ranking algorithms. It does not own orchestration, batch IO, or the curated QA dataset.

## 1. Extraction architecture

```text
raw text + resources
→ high-precision rule extractor
→ LLM structured extractor
→ entity proposals
```

Both extractors return the same internal `Entity` schema. The LLM extractor may return assertions directly. The assertion post-processor corrects only high-confidence contextual cues.

## 2. Rule extractor responsibilities

Rule extraction is Model-owned because it makes semantic label decisions.

Expected deterministic capabilities:

- medicine mentions with dose/unit/form patterns;
- known drug/diagnosis abbreviations with safe dictionary matches;
- lab test names and adjacent results;
- explicit negation/history/family context cues;
- exact source-span positions.

Rules should prefer precision over coverage. The LLM handles context that cannot be safely expressed as deterministic patterns.

## 3. LLM extractor responsibilities

The fixed LLM is `vicuna:7b-v1.5-q5_1` through Ollama.

Input:

- original note;
- optional rule proposals/hints;
- strict label definitions;
- exact output JSON schema;
- selected few-shot examples.

Output:

- exact entity text;
- type;
- assertions;
- optional internal confidence/reason fields that are removed before submission.

Constraints:

- do not normalize or translate final entity text;
- do not invent absent entities;
- do not output ontology codes;
- return an empty list when no entity is present;
- use temperature near zero;
- retry invalid JSON at most once before fallback.

## 4. Assertion handling

The LLM returns assertion values. Deterministic post-processing may override only explicit local cues such as:

- negation near the entity;
- family-subject cues;
- historical-context cues.

The post-processor must use a bounded context window and avoid applying one cue to unrelated entities in another clause.

## 5. Dense retrieval

The fixed embedding model is `bge-m3` through Ollama's embedding endpoint.

Build phase:

1. Embed each alias independently.
2. Convert to `float32` NumPy arrays.
3. Normalize each vector once.
4. Store vector-row metadata.
5. Persist a manifest with model name, dimension, data checksum, and build commit.

Query phase:

1. Normalize/expand the query internally.
2. Embed and normalize the query.
3. Use matrix multiplication for exact cosine search.
4. Return top alias rows.

Exact search is the correctness baseline for HNSW.

## 6. Sparse retrieval

Implement from foundational Python/NumPy structures. Recommended order:

1. exact normalized alias/code match;
2. token BM25;
3. character n-gram TF-IDF or similarity for spelling/unit variants.

Do not use scikit-learn, rank-bm25, Elasticsearch, or another search engine as the project implementation.

Sparse indexes must expose deterministic `fit/build`, `search`, and serialization interfaces.

## 7. Code-level aggregation

Dense and sparse systems rank aliases. Before RRF, keep the best rank/evidence per code in each retrieval channel. This prevents codes with many aliases from receiving unfair repeated votes.

Evidence stored internally:

- matched alias;
- alias type/quality;
- dense rank/score;
- sparse rank/score;
- exact-match flag.

## 8. Reciprocal Rank Fusion

For rank `r` and constant `k`:

```text
RRF contribution = 1 / (k + r)
```

Use one contribution per code per ranking. `k`, retrieval depths, and final candidate count are configuration values and must be evaluated rather than hard-coded throughout modules.

## 9. Optional LLM reranker

Only after RRF is stable:

- send the exact mention, short context, and top retrieved candidates;
- allow selection/reordering only by candidate index;
- reject invented code/index values;
- fallback to RRF order on any error;
- compare metrics before merging.

## 10. HNSW

The team implements HNSW directly.

Required theoretical behavior:

- random node level distribution;
- sparse upper layers and dense layer 0;
- entry point and maximum layer;
- greedy descent on upper layers;
- `ef_construction` candidate search during insertion;
- `ef_search` candidate search during query;
- bidirectional connections;
- degree limits `M` and `M0`;
- distance-based neighbor pruning;
- exact-search comparison.

Not required for core:

- delete/update;
- concurrent insertion;
- GPU kernels;
- C++/Numba optimization;
- production memory layout;
- metadata filters.

## 11. Evaluation

Compare:

- sparse only;
- exact dense only;
- dense + sparse + RRF;
- RRF + optional reranker;
- exact dense versus HNSW.

Metrics:

- Recall@1, @5, @10;
- MRR;
- average and percentile latency;
- HNSW recall relative to exact top-k;
- index build time and memory estimate.

Every benchmark records configuration, data/index checksum, model names, hardware, timestamp, and commit.
