import hashlib
import numpy as np
import multiprocessing as mp



def union(M, N):
    duplicateKeys = set(M.M.keys()).intersection(set(N.M.keys()))
    unionHyperloglogCounter = HyperloglogCounter()
    if len(M.M.keys()) == len(duplicateKeys):
        maxCounts = [(k, max(M.M[k], N.M[k])) for k in duplicateKeys]
        unionHyperloglogCounter.M.update(maxCounts)
        return unionHyperloglogCounter
    else:
        maxCounts = [(k, max(M.M[k], N.M[k])) for k in duplicateKeys]
        unionHyperloglogCounter.M.update(M.M)
        unionHyperloglogCounter.M.update(N.M)
        unionHyperloglogCounter.M.update(maxCounts)
        return unionHyperloglogCounter


def different(a, b):
    duplicateKeys = set(a.M.keys()).intersection(set(b.M.keys()))
    if len(a.M.keys()) != len(duplicateKeys): return True
    different = False
    for k in duplicateKeys:
        if a.M[k] != b.M[k]:
            different = True
            break
    return different

#counter = counters[v]
#connected_counters = all counters[w] for v -> w
def updateCounters(v, counter, connected_counters):
    a = counter.copy()
    for c in connected_counters:
        a = union(c, a) 
    is_different = different(a, counter)
    if is_different:
        return (v, a)

class HyperloglogCounter:
    def __init__(self):
        self.b = 4
        self.p = 2**self.b
        self.alpha = 0.673 # https://en.wikipedia.org/wiki/HyperLogLog#Algorithm
        self.M = dict()

    #return h_p as an integer and h^p as binaryString
    def h(self, x):
        binaryString = '{:0256b}'.format(int.from_bytes(hashlib.sha256(f"{x}".encode('utf8')).digest(), 'little'))
        h_p = int(binaryString[:self.b], 2)
        hp = binaryString[self.b:]
        return h_p, hp

    def pplus(self, h):
        c = 0
        for char in h:
            c += 1
            if char == "1":
                break
        return c

    def add(self, x):
        i, h = self.h(x)
        self.M[i] = max(self.M.get(i, 0),self.pplus(h))

    def size(self):
        if len(self.M) != self.p:   # Because in the algorithm it is specified that initially all M[i] are set to -inf
            Z = 0
        else:
            Z = np.sum(list(map(lambda x: 2**-x, self.M.values())))
            Z = Z**-1

        return self.alpha * self.p**2 * Z

    def copy(self):
        counter = HyperloglogCounter()
        counter.M = dict(self.M)
        return counter


class Hyperball:
    def __init__(self) -> None:
        self.counters = dict()

    def reset(self):
        self.counters = dict()

    def getNewCounterWithVertice(self, v):
        counter = HyperloglogCounter()
        counter.add(v)
        return counter

    # graph G is a dictionary of V -> W
    def run(self, graph, centrality='h'):
        V, E = graph
        accum = dict()
        for v in V:
            counter = self.getNewCounterWithVertice(v)
            self.counters[v] = counter
            accum[v] = 0

        t = 0
        finished = False
        pool = mp.Pool()
        while (not finished):
            result = []

            result = pool.starmap(updateCounters, [(v, self.counters[v], [self.counters[w] for w in E.get(v, set())]) for v in V])

            t += 1

            updated = 0
            for r in result:
                if r is not None:
                    (v, a) = r
                    if centrality == 'c':
                        accum[v] += t * (a.size() - self.counters[v].size())
                    else:
                        accum[v] += (1/t) * (a.size() - self.counters[v].size())
                    self.counters[v] = a
                    updated += 1


            if updated == 0:
                finished = True
            else:
                print(f"iteration: {t}, changed counters: {updated}")
        
        result = dict()
        if centrality == 'c':
            for v in V:
                result[v] = (len(V) - 1) / accum[v] if accum[v] != 0 else "inf"
        else:
            for v in V:
                result[v] = accum[v] / (len(V) - 1)

        return result

            



