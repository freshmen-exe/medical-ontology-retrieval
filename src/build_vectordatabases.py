#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
from collection import Collection
from embed import EmbeddingClient


class VectorBase:
    def __init__(self, dim=1024, max_n=5000000) -> None:
        self.dim = dim
        self.max_n = max_n
        self.sz = 0
        self.vecs = np.empty((max_n, dim), dtype=np.float32)
        self.codes = np.empty(max_n, dtype=np.int32)

    def add(self, vecs, codes) -> None:
        n = vecs.shape[0]

        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1e-9

        norm_vecs = np.ascontiguousarray(vecs / norms, dtype=np.float32)
        start = self.sz
        end = start + n

        self.vecs[start:end] = norm_vecs
        self.codes[start:end] = np.asarray(codes, dtype=np.int32)
        self.sz = end

    def save(self, dir) -> None:
        os.makedirs(dir, exist_ok=True)
        np.save(os.path.join(dir, "vecs.npy"), self.vecs[: self.sz])
        np.save(os.path.join(dir, "codes.npy"), self.codes[: self.sz])
        with open(os.path.join(dir, "meta.txt"), "w", encoding="locale") as f:
            f.write(f"{self.dim},{self.sz},{self.max_n}")

    def load(self, dir) -> None:
        with open(os.path.join(dir, "meta.txt"), encoding="locale") as f:
            self.dim, self.sz, self.max_n = map(int, f.read().split(","))

            self.vecs = np.load(os.path.join(dir, "vecs.npy"), mmap_mode="r")
            self.codes = np.load(os.path.join(dir, "codes.npy"), mmap_mode="r")


ROOT_DIR = Path(__file__).resolve().parents[1]
LIBS_DIR = ROOT_DIR / "src" / "libs"
sys.path.insert(0, str(LIBS_DIR))


JsonObject = dict[str, Any]

ICD_SOURCES = {
    "icd_chapter": ROOT_DIR / "data" / "icd_data" / "processed_data" / "chapter.json",
    "icd_section": ROOT_DIR / "data" / "icd_data" / "processed_data" / "section.json",
    "icd_category": ROOT_DIR / "data" / "icd_data" / "processed_data" / "category.json",
    "icd_sub_category": ROOT_DIR / "data" / "icd_data" / "processed_data" / "sub-category.json",
}
RXNORM_SOURCE = ROOT_DIR / "data" / "rxnorm_data" / "rxnorm_processed_alias.json"


def load_icd_records(path: Path) -> list[JsonObject]:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)

    records = payload.get("array")
    if not isinstance(records, list):
        msg = f"{path} must contain an array field"
        raise TypeError(msg)
    return records


def load_rxnorm_records(path: Path) -> list[JsonObject]:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, list):
        msg = f"{path} must contain a JSON list"
        raise TypeError(msg)
    return payload


def icd_text(record: JsonObject) -> str:
    code = str(record.get("id", ""))
    text = str(record.get("text", ""))
    return f"Instruct: Retrieve an ICD-10 concept. Query: {code} {text}".strip()


def rxnorm_text(record: JsonObject) -> str:
    name_vi = str(record.get("name_vi", ""))
    name_en = str(record.get("name_en", ""))
    term_type = str(record.get("term_type", ""))
    return f"Instruct: Retrieve an RxNorm drug concept. Query: {name_vi} {name_en} {term_type}".strip()


def build_collection(
    name: str,
    records: list[JsonObject],
    texts: list[str],
    output_root: Path,
    embedder: EmbeddingClient,
    dim: int,
    m: int,
    efc: int,
    efs: int,
) -> None:
    vecs = embedder.embed_texts(texts)
    if vecs.ndim != 2:
        msg = f"{name} embeddings must be a 2D matrix"
        raise ValueError(msg)
    if vecs.shape[1] != dim:
        msg = f"{name} embedding dim is {vecs.shape[1]}, expected {dim}"
        raise ValueError(msg)

    collection = Collection(dim=dim, max_n=max(len(records), 1), m=m, efc=efc, efs=efs)
    collection.add(np.ascontiguousarray(vecs, dtype=np.float32), records)
    collection.build()
    collection.save(output_root / name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build ICD and RxNorm vector databases.")
    parser.add_argument("--output", type=Path, default=ROOT_DIR / "data" / "vectordatabase")
    parser.add_argument("--dim", type=int, default=int(os.environ.get("EMBEDDING_DIMENSION", "1024")))
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--m", type=int, default=20)
    parser.add_argument("--efc", type=int, default=200)
    parser.add_argument("--efs", type=int, default=50)
    parser.add_argument("--embedding-base-url", default=None)
    parser.add_argument("--embedding-api-key", default=None)
    parser.add_argument("--embedding-model", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    embedder = EmbeddingClient(
        base_url=args.embedding_base_url,
        api_key=args.embedding_api_key,
        model=args.embedding_model,
        batch_size=args.batch_size,
    )

    for name, path in ICD_SOURCES.items():
        records = load_icd_records(path)
        build_collection(
            name=name,
            records=records,
            texts=[icd_text(record) for record in records],
            output_root=args.output,
            embedder=embedder,
            dim=args.dim,
            m=args.m,
            efc=args.efc,
            efs=args.efs,
        )

    rxnorm_records = load_rxnorm_records(RXNORM_SOURCE)
    build_collection(
        name="rxnorm",
        records=rxnorm_records,
        texts=[rxnorm_text(record) for record in rxnorm_records],
        output_root=args.output,
        embedder=embedder,
        dim=args.dim,
        m=args.m,
        efc=args.efc,
        efs=args.efs,
    )


if __name__ == "__main__":
    main()
