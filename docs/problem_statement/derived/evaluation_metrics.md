# Evaluation Metrics

The official scoring formula recorded from the task statement is:

```text
final_score = 0.3 × text_score
            + 0.3 × assertions_score
            + 0.4 × candidates_score
```

A wrong entity type can reduce the relevant score, so extraction, classification, assertion handling,
and mapping must be evaluated separately rather than hiding all errors behind an end-to-end number.

## Local metrics

Extraction:

- exact-span entity precision, recall, and F1;
- label correctness;
- schema pass rate.

Assertions:

- accuracy/F1 for negation, family, and history on applicable entities.

Retrieval:

- Recall@1, Recall@5, Recall@10;
- Mean Reciprocal Rank;
- exact-vs-HNSW Recall@k;
- latency per query and per note.

End to end:

- candidate hit@k on correctly extracted diagnosis/drug mentions;
- official-style component scores when the complete organizer evaluator is available.

Local metrics are diagnostics and must not be represented as the official leaderboard score unless
the implementation exactly matches the organizer evaluator.
