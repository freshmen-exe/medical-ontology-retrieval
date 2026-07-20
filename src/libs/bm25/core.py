#!/usr/bin/env python3
import os
import pickle
import re

import numpy as np
from numba import njit


@njit(fastmath=True)
def search(q_term_ids, term_ptrs, doc_ids, weights, num_docs):
    scores = np.zeros(num_docs, dtype=np.float32)

    for term_id in q_term_ids:
        start_idx = term_ptrs[term_id]
        end_idx = term_ptrs[term_id + 1]
        for i in range(start_idx, end_idx):
            scores[doc_ids[i]] += weights[i]

    return scores


class BM25:
    def __init__(self, k1=1.5, b=0.75, delta=1.0) -> None:
        self.k1 = k1
        self.b = b
        self.delta = delta

        self.pattern = re.compile(r"(?u)\b[\w.-]+\b")

        self.vocab = {}
        self.num_docs = 0
        self.docs = []

        self.term_ptrs = None
        self.doc_ids = None
        self.weights = None

    def build(self, corpus) -> None:
        self.docs = corpus
        self.num_docs = len(corpus)
        self.vocab = {}

        doc_ids = np.array([], dtype=np.int32)
        term_ids = np.array([], dtype=np.int32)
        term_freqs = np.array([], dtype=np.int32)

        for doc_id, text in enumerate(corpus):
            tks = self.pattern.findall(text.lower())

            cnts = {}
            for tk in tks:
                cnts[tk] = cnts.get(tk, 0) + 1

            for tk, cnt in cnts.items():
                if tk not in self.vocab:
                    self.vocab[tk] = len(self.vocab)

                term_ids.append(self.vocab[tk])
                doc_ids.append(doc_id)
                term_freqs.append(cnt)

        vocab_sz = len(self.vocab)

        doc_lens = np.zeros(self.num_docs, dtype=np.float32)
        np.add.at(doc_lens, doc_ids, term_freqs)
        avgdl = np.mean(doc_lens)

        doc_freqs = np.zeros(vocab_sz, dtype=np.int32)
        np.add.at(doc_freqs, term_ids, 1)

        idfs = np.log(1.0 + (self.num_docs - doc_freqs + 0.5) / (doc_freqs + 0.5))
        len_norm = (1.0 - self.b) + self.b * (doc_lens[doc_ids] / avgdl)
        idf = idfs[term_ids]

        weights = idf * ((term_freqs * (self.k1 + 1.0)) / (term_freqs + self.k1 * len_norm) + self.delta)

        sort_idx = np.argsort(term_ids)

        self.doc_ids = doc_ids[sort_idx]
        self.weights = weights[sort_idx]

        self.term_ptrs = np.zeros(vocab_sz + 1, dtype=np.int32)
        self.term_ptrs[1:] = np.cumsum(doc_freqs)

    def search(self, q, k=5):
        if not self.vocab:
            return [], []

        tks = self.pattern.findall(q.lower())

        q_term_ids = [self.vocab[tk] for tk in tks if tk in self.vocab]
        if not q_term_ids:
            return [], []

        q_term_ids = np.array(q_term_ids, dtype=np.int32)
        scores = search(q_term_ids, self.term_ptrs, self.doc_ids, self.weights, self.num_docs)

        k = min(k, np.count_nonzero(scores))
        if not k:
            return [], []

        top_k_idx = np.argpartition(scores, -k)[-k:]
        top_k_idx = top_k_idx[np.argsort(scores[top_k_idx])[::-1]]

        res_docs = [self.docs[idx] for idx in top_k_idx]
        res_scores = scores[top_k_idx]

        return res_docs, res_scores

    def save(self, dir) -> None:
        os.makedirs(dir, exist_ok=True)
        np.savez_compressed(os.path.join(dir, "bm25_arr.npz"), term_ptrs=self.term_ptrs, doc_ids=self.doc_ids, weights=self.weights)
        with open(os.path.join(dir, "bm25_meta.pkl"), "wb") as f:
            pickle.dump({"vocab": self.vocab, "docs": self.docs, "num_docs": self.num_docs}, f)

    def load(self, dir) -> None:
        data = np.load(os.path.join(dir, "bm25_arr.npz"))
        self.term_ptrs = data["term_ptrs"]
        self.doc_ids = data["doc_ids"]
        self.weights = data["weights"]

        with open(os.path.join(dir, "bm25_meta.pkl"), "rb") as f:
            meta = pickle.load(f)
            self.vocab = meta["vocab"]
            self.docs = meta["docs"]
            self.num_docs = meta["num_docs"]
