#!/usr/bin/env python3
import json
import os
import re
from collections.abc import Sequence
from typing import TypeAlias

import requests

RerankCandidate: TypeAlias = dict[str, object]


def _candidate_key(candidate: RerankCandidate) -> str:
    code = candidate.get("code")
    if code is not None:
        return str(code)

    identifier = candidate.get("id")
    if identifier is not None:
        return str(identifier)

    return json.dumps(candidate, ensure_ascii=False, sort_keys=True)


def rrf_fuse(
    dense_results: Sequence[RerankCandidate],
    sparse_results: Sequence[RerankCandidate],
    *,
    rrf_k: int = 60,
    limit: int | None = None,
) -> list[RerankCandidate]:
    """Fuse dense and sparse rankings with Reciprocal Rank Fusion.

    RRF only uses rank positions. Dense/sparse score values are preserved for
    debugging, but they do not affect the fused rank.
    """
    candidates_by_key: dict[str, RerankCandidate] = {}
    scores_by_key: dict[str, float] = {}
    dense_rank_by_key: dict[str, int] = {}
    sparse_rank_by_key: dict[str, int] = {}

    for source_name, results, rank_by_key in (
        ("dense", dense_results, dense_rank_by_key),
        ("sparse", sparse_results, sparse_rank_by_key),
    ):
        seen_keys: set[str] = set()
        for rank, candidate in enumerate(results, start=1):
            key = _candidate_key(candidate)
            if key in seen_keys:
                continue

            seen_keys.add(key)
            rank_by_key[key] = rank
            scores_by_key[key] = scores_by_key.get(key, 0.0) + 1.0 / (rrf_k + rank)

            if key not in candidates_by_key:
                candidates_by_key[key] = dict(candidate)

            candidates_by_key[key][f"{source_name}_rank"] = rank

    ranked_keys = sorted(
        scores_by_key,
        key=lambda key: (
            -scores_by_key[key],
            dense_rank_by_key.get(key, 10**9),
            sparse_rank_by_key.get(key, 10**9),
            key,
        ),
    )

    if limit is not None:
        ranked_keys = ranked_keys[:limit]

    fused: list[RerankCandidate] = []
    for rank, key in enumerate(ranked_keys, start=1):
        candidate = dict(candidates_by_key[key])
        candidate["rrf_rank"] = rank
        candidate["rrf_score"] = scores_by_key[key]
        fused.append(candidate)

    return fused


class LLMReranker:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 20.0,
    ) -> None:
        self.base_url = base_url or os.environ.get("LLM_BASE_URL", "http://localhost:8080/v1")
        self.api_key = api_key or os.environ.get("LLM_API_KEY", "local-internal-key")
        self.model = model or os.environ.get("LLM_MODEL", "medical-extractor")
        self.timeout = timeout

    def rerank(
        self,
        query: str,
        entity_type: str,
        candidates: Sequence[RerankCandidate],
        *,
        top_k: int = 5,
    ) -> list[RerankCandidate]:
        if not candidates:
            return []

        try:
            selected_keys = self._request_rerank(query, entity_type, candidates, top_k)
        except Exception:
            return [dict(candidate) for candidate in candidates[:top_k]]

        candidate_by_key = {_candidate_key(candidate): candidate for candidate in candidates}
        reranked: list[RerankCandidate] = []
        seen_keys: set[str] = set()

        for key in selected_keys:
            if key in seen_keys or key not in candidate_by_key:
                continue
            candidate = dict(candidate_by_key[key])
            candidate["llm_rank"] = len(reranked) + 1
            reranked.append(candidate)
            seen_keys.add(key)
            if len(reranked) >= top_k:
                return reranked

        for candidate in candidates:
            key = _candidate_key(candidate)
            if key in seen_keys:
                continue
            fallback_candidate = dict(candidate)
            fallback_candidate["llm_rank"] = len(reranked) + 1
            reranked.append(fallback_candidate)
            if len(reranked) >= top_k:
                break

        return reranked

    def _request_rerank(
        self,
        query: str,
        entity_type: str,
        candidates: Sequence[RerankCandidate],
        top_k: int,
    ) -> list[str]:
        prompt = self._build_prompt(query, entity_type, candidates, top_k)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a medical ontology reranker. Return strict JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        content = str(data["choices"][0]["message"]["content"])
        parsed = _parse_json_object(content)
        raw_results = parsed.get("results", [])
        if not isinstance(raw_results, list):
            return []

        keys: list[str] = []
        for item in raw_results:
            if isinstance(item, str):
                keys.append(item)
            elif isinstance(item, dict):
                code = item.get("code")
                identifier = item.get("id")
                if code is not None:
                    keys.append(str(code))
                elif identifier is not None:
                    keys.append(str(identifier))

        return keys[:top_k]

    def _build_prompt(
        self,
        query: str,
        entity_type: str,
        candidates: Sequence[RerankCandidate],
        top_k: int,
    ) -> str:
        payload_candidates: list[dict[str, object]] = [
            {
                "code": candidate.get("code"),
                "id": candidate.get("id"),
                "name": candidate.get("name"),
                "text": candidate.get("text"),
                "rrf_rank": candidate.get("rrf_rank"),
                "dense_rank": candidate.get("dense_rank"),
                "sparse_rank": candidate.get("sparse_rank"),
            }
            for candidate in candidates
        ]

        return (
            "Rerank các ứng viên ontology y khoa cho query sau.\n"
            "Chỉ dựa vào mức độ khớp y khoa giữa query và candidate. RRF rank là tín hiệu ưu tiên ban đầu.\n"
            f"Query: {query}\n"
            f"Entity type: {entity_type}\n"
            f"Chọn tối đa {top_k} ứng viên tốt nhất.\n"
            'Trả về JSON đúng dạng: {"results": [{"code": "..."}]}.\n'
            f"Candidates: {json.dumps(payload_candidates, ensure_ascii=False)}"
        )


def _parse_json_object(content: str) -> dict[str, object]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            return {}
        parsed = json.loads(match.group(0))

    if isinstance(parsed, dict):
        return parsed
    return {}
