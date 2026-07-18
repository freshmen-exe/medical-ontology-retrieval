import os

import numpy as np
from heap import Heap
from numba import float16, float32, int8, int32, njit, prange, uint16
from numba.experimental import jitclass

hnsw_core_spec = [
    ("vecs", float16[:, ::1]),
    ("g0", int32[:, ::1]),
    ("gh_id", int32[::1]),
    ("gh", int32[:, :, ::1]),
    ("lvs", int8[::1]),
    ("m", int32),
    ("m0", int32),
    ("efc", int32),
    ("efs", int32),
    ("ml", float32),
    ("max_lv", int32),
    ("ep", int32),
    ("h_sz", int32),
    ("vis", uint16[:, ::1]),
    ("vis_tags", uint16[::1]),
    ("bd_vis", uint16[::1]),
    ("bd_tag", uint16),
    ("sz", int32),
]


@jitclass(hnsw_core_spec)
class HNSWCore:
    MAX_LV = 5

    def __init__(self, vecs, g0, gh_id, gh, lvs, m, m0, efc, efs, ml, vis, vis_tags, bd_vis, sz) -> None:
        self.vecs = vecs
        self.g0 = g0
        self.gh_id = gh_id
        self.gh = gh
        self.lvs = lvs
        self.m = m
        self.m0 = m0
        self.efc = efc
        self.efs = efs
        self.ml = ml
        self.max_lv = -1
        self.ep = -1
        self.h_sz = 0
        self.vis = vis
        self.vis_tags = vis_tags
        self.bd_vis = bd_vis
        self.bd_tag = 1
        self.sz = sz

    def select(self, cand_ids, cand_dists, max_m):
        idx = np.argsort(cand_dists)
        ids = cand_ids[idx]
        dists = cand_dists[idx]

        res = np.full(max_m, -1, dtype=np.int32)
        cnt = 0

        for i in range(len(ids)):
            if cnt >= max_m:
                break
            cand_id = ids[i]
            cand_dist = dists[i]
            keep = True
            for res_idx in range(cnt):
                res_id = res[res_idx]
                dist = 1 - np.dot(self.vecs[cand_id], self.vecs[res_id])
                if dist > cand_dist:
                    keep = False
                    break
            if keep:
                res[cnt] = cand_id
                cnt += 1

        return res[res != -1]

    def search_layer(self, q, ep, ef, lv, is_bd, b_id):
        cand = Heap(100000, 0)
        near = Heap(ef + 1, 1)
        dist_ep = 1 - np.dot(self.vecs[ep], q)
        if is_bd:
            self.bd_vis[ep] = self.bd_tag
        else:
            self.vis[b_id, ep] = self.vis_tags[b_id]

        cand.push(dist_ep, ep)
        near.push(dist_ep, ep)

        while cand.sz:
            cand_dist, cand_id = cand.pop()
            if near.sz and cand_dist > near.dists[0]:
                break
            if not lv:
                adj = self.g0[cand_id]
            else:
                h_id = self.gh_id[cand_id]
                adj = self.gh[h_id, lv] if h_id != -1 else np.empty(0, dtype=np.int32)

            for u in adj:
                if u == -1:
                    break
                is_vis = False
                if is_bd:
                    if self.bd_vis[u] == self.bd_tag:
                        is_vis = True
                    else:
                        self.bd_vis[u] = self.bd_tag
                elif self.vis[b_id, u] == self.vis_tags[b_id]:
                    is_vis = True
                else:
                    self.vis[b_id, u] = self.vis_tags[b_id]

                if not is_vis:
                    dist = 1 - np.dot(self.vecs[u], q)
                    if near.sz < ef or dist < near.dists[0]:
                        cand.push(dist, u)
                        near.push(dist, u)
                        if near.sz > ef:
                            near.pop()
        res_dists = np.empty(near.sz, dtype=np.float32)
        res_ids = np.empty(near.sz, dtype=np.int32)
        idx = near.sz - 1

        while near.sz:
            dist, id = near.pop()
            res_dists[idx] = dist
            res_ids[idx] = id
            idx -= 1

        return res_dists, res_ids

    def build(self) -> None:
        for id in range(self.sz):
            q = np.ascontiguousarray(self.vecs[id])
            lv = min(self.MAX_LV - 1, int(-np.log(np.random.rand()) * self.ml))
            self.lvs[id] = lv

            if self.ep == -1:
                self.ep = id
                self.max_lv = lv
                continue

            if lv:
                self.gh_id[id] = self.h_sz
                self.h_sz += 1

            cur = self.ep
            for _lv in range(self.max_lv, lv, -1):
                self.bd_tag += 1
                _, ids = self.search_layer(q, cur, 1, _lv, 1, 0)
                cur = ids[0] if len(ids) else cur

            for _lv in range(min(lv, self.max_lv), -1, -1):
                self.bd_tag += 1
                cand_dists, cand_ids = self.search_layer(q, cur, self.efc, _lv, 1, 0)

                max_m = self.m0 if not _lv else self.m
                adj = self.select(cand_ids, cand_dists, max_m)

                if not _lv:
                    self.g0[id, : len(adj)] = adj
                else:
                    h_id = self.gh_id[id]
                    self.gh[h_id, _lv, : len(adj)] = adj

                for u in adj:
                    if not _lv:
                        valid = self.g0[u][self.g0[u] != -1]
                        if len(valid) < self.m0:
                            self.g0[u, len(valid)] = id
                        else:
                            all_cand = np.append(valid, id)
                            all_dists = np.empty(len(all_cand), dtype=np.float32)
                            for c_idx in range(len(all_cand)):
                                c = all_cand[c_idx]
                                all_dists[c_idx] = 1 - np.dot(self.vecs[u], self.vecs[c])
                            best = self.select(all_cand, all_dists, self.m0)
                            self.g0[u] = np.full(self.m0, -1, dtype=np.int32)
                            self.g0[u, : len(best)] = best
                    else:
                        h_id = self.gh_id[u]
                        valid = self.gh[h_id, _lv][self.gh[h_id, _lv] != -1]
                        if len(valid) < self.m:
                            self.gh[h_id, _lv, len(valid)] = id
                        else:
                            all_cand = np.append(valid, id)
                            all_dists = np.empty(len(all_cand), dtype=np.float32)
                            for c_idx in range(len(all_cand)):
                                c = all_cand[c_idx]
                                all_dists[c_idx] = 1 - np.dot(self.vecs[u], self.vecs[c])
                            best = self.select(all_cand, all_dists, self.m)
                            self.gh[h_id, _lv] = np.full(self.m, -1, dtype=np.int32)
                            self.gh[h_id, _lv, : len(best)] = best

                cur = cand_ids[np.argmax(cand_dists)] if len(cand_ids) else cur

            if lv > self.max_lv:
                self.max_lv = lv
                self.ep = id


@njit(parallel=True, fastmath=True)
def search(self, qs, k):
    b_sz = qs.shape[0]
    res_dists = np.zeros((b_sz, k), dtype=np.float32)
    res_ids = np.zeros((b_sz, k), dtype=np.int32)

    for b_id in prange(b_sz):
        q = qs[b_id]
        self.vis_tags[b_id] += 1
        cur = self.ep

        for lv in range(self.max_lv, 0, -1):
            best_id = cur
            best_dist = 1 - np.dot(self.vecs[cur], q)
            changed = True
            while changed:
                changed = False
                h_id = self.gh_id[best_id]
                if h_id != -1:
                    adj = self.gh[h_id, lv]
                    for u in adj:
                        if u == -1:
                            break
                        dist = 1 - np.dot(self.vecs[u], q)
                        if dist < best_dist:
                            best_dist = dist
                            best_id = u
                            changed = True
            cur = best_id

        dists, ids = self.search_layer(q, cur, self.efs, 0, 0, b_id)

        take = min(k, len(ids))
        res_dists[b_id, :take] = dists[:take]
        res_ids[b_id, :take] = ids[:take]

    return res_dists, res_ids


class HNSW:
    def __init__(self, vb, m=20, efc=200, efs=50, b_sz=100) -> None:
        self.MAX_LV = 5
        self.vb = vb
        self.b_sz = b_sz

        n = self.vb.max_n
        m0 = m * 2
        ml = np.float32(1.0 / np.log(m))
        lvs = np.zeros(n, dtype=np.int8)
        g0 = np.full((n, m0), -1, dtype=np.int32)
        gh_id = np.full(n, -1, dtype=np.int32)

        max_hn = n // m * 2
        gh = np.full((max_hn, self.MAX_LV, m), -1, dtype=np.int32)
        vis = np.zeros((b_sz, n), dtype=np.uint16)
        vis_tags = np.ones(b_sz, dtype=np.uint16)
        bd_vis = np.zeros(n, dtype=np.uint16)

        self.core = HNSWCore(self.vb.vecs, g0, gh_id, gh, lvs, m, m0, efc, efs, ml, vis, vis_tags, bd_vis, self.vb.sz)

    def build(self) -> None:
        self.core.sz = self.vb.sz
        self.core.build()

    def search(self, qs, k=5):
        if self.core.ep == -1:
            return [], []

        norms = np.linalg.norm(qs, axis=1, keepdims=True)
        norms[norms == 0] = 1e-9
        norm_qs = np.ascontiguousarray(qs / norms, dtype=np.float32)

        norm_qs.shape[0]
        dists, ids = search(self.core, norm_qs, k)
        return dists, self.vb.codes[ids]

    def save(self, dir) -> None:
        os.makedirs(dir, exist_ok=True)
        meta = np.array([self.core.ep, self.core.max_lv, self.core.h_sz, self.core.sz], dtype=np.int32)
        np.savez_compressed(
            os.path.join(dir, "hnsw.npz"),
            meta=meta,
            lvs=self.core.lvs,
            g0=self.core.g0,
            gh_id=self.core.gh_id,
            gh=self.core.gh[: self.core.h_sz],
        )

    def load(self, dir) -> None:
        data = np.load(os.path.join(dir, "hnsw.npz"))
        self.core.ep, self.core.max_lv, self.core.h_sz, self.core.sz = data["meta"]
        self.core.lvs = data["lvs"]
        self.core.g0 = data["g0"]
        self.core.gh_id = data["gh_id"]
        gh = data["gh"]
        max_hn = self.vb.max_n // self.core.m * 2
        self.core.gh = np.full((max_hn, self.MAX_LV, self.core.m), -1, dtype=np.int32)
        self.core.gh[: self.core.h_sz] = gh
