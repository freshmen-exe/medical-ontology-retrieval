import numpy as np
from numba import float32, int32
from numba.experimental import jitclass

heap_spec = [("dists", float32[:]), ("ids", int32[:]), ("sz", int32), ("max_heap", int32)]


@jitclass(heap_spec)
class Heap:
    def __init__(self, cap, max_heap=1) -> None:
        self.dists = np.empty(cap, dtype=np.float32)
        self.ids = np.empty(cap, dtype=np.int32)
        self.sz = 0
        self.max_heap = max_heap

    def clear(self) -> None:
        self.sz = 0

    def push(self, dist, id) -> None:
        i = self.sz
        self.sz += 1
        while i:
            par = (i - 1) >> 1
            if self.max_heap:
                if self.dists[par] >= dist:
                    break
            elif self.dists[par] <= dist:
                break
            self.dists[i], self.ids[i] = self.dists[par], self.ids[par]
            i = par
        self.dists[i], self.ids[i] = dist, id

    def pop(self):
        res_dist, res_id = self.dists[0], self.ids[0]
        self.sz -= 1
        if not self.sz:
            return res_dist, res_id
        dist, id = self.dists[self.sz], self.ids[self.sz]
        i = 0
        while (i << 1) + 1 < self.sz:
            left = (i << 1) + 1
            right = left + 1
            tar = left
            if self.max_heap:
                if right < self.sz and self.dists[right] > self.dists[left]:
                    tar = right
                if dist >= self.dists[tar]:
                    break
            else:
                if right < self.sz and self.dists[right] < self.dists[left]:
                    tar = right
                if dist <= self.dists[tar]:
                    break

            self.dists[i], self.ids[i] = self.dists[tar], self.ids[tar]
            i = tar

        self.dists[i], self.ids[i] = dist, id
        return res_dist, res_id
