import random
import zlib

# document being a long string 
def shingle(document, k=10):
    result = set()
    # preparing the text
    text = ''.join(document.split()).lower()
    text = text.replace('!', '').replace(',', '').replace('.', '').replace('?', '').replace('"', '')
    #generating the hashed shingles
    for i in range(len(text) - k + 1):
        shingle = text[i:(i+k)]
        result.add(zlib.adler32(shingle.encode('utf8')))
    return result

#computes the Jaccard similarity of two shingled documents
def compareSets(set1: set, set2: set):
    union = set.union(set1, set2)
    intersection = set.intersection(set1, set2)
    return len(intersection) / len(union)

def compare_signatures(sig1, sig2):
    equal = 0
    assert len(sig1) == len(sig2)
    for s1, s2 in zip(sig1, sig2):
        equal += 1 if s1 == s2 else 0
    return equal / len(sig1)

class MinHash:
    def __init__(self, n=100) -> None:
        self.n_hash_functions = n
        self.c = 2**32 - 1
        self.a = random.sample(range(0, self.c), n)
        self.b = random.sample(range(0, self.c), n)
        self.hash_function = lambda x, i: (self.a[i]*x + self.b[i]) % self.c

    def create_signature(self, hashes):
        signature = list()
        for i in range(self.n_hash_functions):
            s = self.c
            for h in hashes:
                s = min(s, self.hash_function(h, i))
            signature.append(s)
        return signature


