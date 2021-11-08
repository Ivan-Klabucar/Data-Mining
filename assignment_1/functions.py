import random
import zlib

# document being a long string 
def shingle(document, k=10):
    result = set()

    words = document.split()
    for i in range(len(words) - k + 1):
        shingle = words[i:(i+k)]
        #lists are mutable hence not hashable which is why we have to create a single string to hash
        shingle_string = ''.join(shingle)
        result.add(zlib.adler32(shingle_string.encode('utf8')))

    return result

#computes the Jaccard similarity of two shingled documents
def compareSets(set1: set, set2: set):
    union = set.union(set1, set2)
    intersection = set.intersection(set1, set2)
    return len(intersection) / len(union)

class MinHash:
    def __init__(self, n=100) -> None:
        self.n_hash_functions = n
        self.c = 2**32 - 1
        self.a = list()
        self.b = list()
        for _ in range(n):
            self.a.append(random.randint(0, self.c))
            self.b.append(random.randint(0, self.c))
        self.hash_function = lambda x, i: (self.a[i]*x + self.b[i]) % self.c

    def create_signature(self, hashes):
        signature = list()
        for i in range(self.n_hash_functions):
            s = self.c
            for h in hashes:
                s = min(s, self.hash_function(h, i))
            signature.append(s)
        return signature


    def compareSets(self, sig1, sig2):
        equal = 0
        for s1, s2 in zip(sig1, sig2):
            equal += 1 if s1 == s2 else 0
        return equal / self.n_hash_functions

