#!/usr/bin/env python3
import json
import os

import numpy as np
from hnsw import HNSW
from vectorbase import VectorBase


class Collection:
    def __init__(self, dim=1024, max_n=5000000, m=20, efc=200, efs=50, b_sz=100) -> None:
        self.vb = VectorBase(dim, max_n)
        self.index = HNSW(self.vb, m=m, efc=efc, efs=efs, b_sz=b_sz)
        self.docs = {}
        self.sess_id = 0

    def add(self, vecs, docs) -> None:
        n = vecs.shape[0]
        ids = np.arange(self.sess_id, self.sess_id + n, dtype=np.int32)
        self.vb.add(vecs, ids)
        for i in range(n):
            self.docs[int(ids[i])] = docs[i]
        self.sess_id += n

    def build(self) -> None:
        self.index.build()

    def search(self, qs, k=10):
        dists, ids = self.index.search(qs, k)
        res = []
        for i in range(len(qs)):
            docs = []
            for j in range(len(ids[i])):
                id = ids[i][j]
                doc = self.docs[id]

                docs.append({"distance": float(dists[i][j]), **doc})
            res.append(docs)
        return res

    def save(self, dir) -> None:
        self.vb.save(dir)
        self.index.save(dir)
        with open(os.path.join(dir, "docs.json"), "w", encoding="utf-8") as f:
            json.dump(self.docs, f, ensure_ascii=False)

    def load(self, dir) -> None:
        self.vb.load(dir)
        self.index.load(dir)
        self.sess_id = self.vb.sz

        with open(os.path.join(dir, "docs.json"), encoding="utf-8") as f:
            docs = json.load(f)
            self.docs = {int(key): val for key, val in docs.items()}
