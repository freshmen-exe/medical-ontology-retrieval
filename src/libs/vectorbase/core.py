#!/usr/bin/env python3
import os

import numpy as np


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
        self.vecs[start : start + n] = norm_vecs
        self.sz += n

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
