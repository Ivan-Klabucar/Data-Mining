import random
import zlib
from functools import reduce
from itertools import combinations

# document being a long string 
def shingle(document, k=10):
    #to remove duplicates we use a set as data structure
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

# here the user has to make sure to only compare signatures made by the same set of hash functions
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
        # building our own hash function (a * x + b) % c
        # to create a "good" hash function should c be a prime, but in this use case we don't care for a very
        # high quality hash function, but for a fast way to shuffle a dataset, hence our choice for should
        # work reasonably well
        self.hash_function = lambda x, i: (self.a[i]*x + self.b[i]) % self.c

    def create_signature(self, hashes):
        signature = list()
        for i in range(self.n_hash_functions):
            s = self.c
            for h in hashes:
                s = min(s, self.hash_function(h, i))
            signature.append(s)
        return signature


class LSH:
    def __init__(self, signatures, num_of_bands, threshold):
        self.sig = signatures
        self.num_of_bands = num_of_bands
        self.threshold = threshold
        self.buckets = dict()
        for k in self.sig: 
            assert len(self.sig[k]) % self.num_of_bands == 0
            self.width_of_band = int(len(self.sig[k]) / self.num_of_bands)
    
    def clear_buckets(self):
        for k in self.buckets:
            self.buckets[k].clear()
    
    def add_to_bucket(self, bucket, candidate):
        if not bucket in self.buckets: self.buckets[bucket] = set()
        self.buckets[bucket].add(candidate)
    
    # to hash a band we simply substring the signature, see it as a string and hash the string 
    def hash_band(self, band):
        reduced_band = reduce(lambda accum, x: f'{accum}{x}', band)
        return zlib.adler32(reduced_band.encode('utf8'))
    
    def get_candidates(self):
        result = set()
        for i in range(self.num_of_bands):
            self.clear_buckets()
            for doc in self.sig:
                #print(f'doc:{doc}, i:{i}, band:{self.sig[doc]}')
                hashed_band = self.hash_band(self.sig[doc][i*self.width_of_band:((i+1)*self.width_of_band)])
                self.add_to_bucket(bucket=hashed_band, candidate=doc)
            for b in self.buckets:
                result.update(set([tuple(sorted(c)) for c in combinations(self.buckets[b],2)]))
        #print(f'Num of candidates: {len(result)}')
        return result
    
    def get_candidates_above_threshold(self, method, data_with_duplicates=False):
        result = set()
        candidates = self.get_candidates()
        for c in candidates:
            first = c[0]
            second = c[1]
            # when we conduct the performance experiments we use duplicates of datasets, so here we have to remove the ending which only
            # tells us which duplicate the respective document is and only use the original name for calculating the similarity
            if data_with_duplicates:
                first = first.split('-')[0]
                second = second.split('-')[0]
            if method(first, second) > self.threshold:
                result.add(c)
        return result
                