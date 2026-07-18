#!/usr/bin/env python3
import os
from typing import TYPE_CHECKING

import numpy as np
import requests

if TYPE_CHECKING:
    from typing import Any


class EmbeddingError(RuntimeError):
    pass


class EmbeddingClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
        batch_size: int = 32,
    ) -> None:
        self.base_url = (base_url or os.environ.get("EMBEDDING_BASE_URL", "http://localhost:8081/v1")).rstrip("/")
        self.api_key = api_key or os.environ.get("EMBEDDING_API_KEY", "local-internal-key")
        self.model = model or os.environ.get("EMBEDDING_MODEL", "qwen3-embedding-0.6b")
        self.timeout = timeout
        self.batch_size = batch_size

    def embed_text(self, text: str) -> np.ndarray:
        vecs = self.embed_texts([text])
        return vecs[0]

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 0), dtype=np.float32)

        batches: list[np.ndarray] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            batches.append(self._embed_batch(batch))

        return np.vstack(batches).astype(np.float32, copy=False)

    def _embed_batch(self, texts: list[str]) -> np.ndarray:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "input": texts,
        }

        response = requests.post(f"{self.base_url}/embeddings", headers=headers, json=payload, timeout=self.timeout)
        if response.status_code != 200:
            msg = f"embedding request failed with status {response.status_code}: {response.text}"
            raise EmbeddingError(msg)

        data = response.json()
        rows = data.get("data")
        if not isinstance(rows, list):
            msg = "embedding response must contain a data list"
            raise EmbeddingError(msg)

        embeddings: list[list[float]] = []
        for row in rows:
            if not isinstance(row, dict) or "embedding" not in row:
                msg = "embedding response row is missing embedding"
                raise EmbeddingError(msg)
            embeddings.append(row["embedding"])

        if len(embeddings) != len(texts):
            msg = "embedding response length does not match input length"
            raise EmbeddingError(msg)

        return np.asarray(embeddings, dtype=np.float32)
