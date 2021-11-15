import itertools
import time


#ITEMSETS ARE TREATED AS TUPLES!
class FrequentItemsetFinder:
    def __init__(self, dataset, s):
        self.freq_itemsets = dict() # 1: set(frequent items), 2: set(frequent pairs)...
        self.dataset = dataset
        self.s = s
        self.N = len(self.dataset)

    def find_freq_items(self): # There's no duplicates in baskets I checked.
        cnt = dict()
        for basket in self.dataset:
            for item in basket:
                if item not in cnt: cnt[item] = 0
                cnt[item] += 1

        self.freq_itemsets[1] = {(item,) for item in cnt if cnt[item] >= (self.s * self.N)}
        return len(self.freq_itemsets[1]) > 0
    
    def check_if_viable_combination(self, itemset, item):          # Check if it makes sense to expand an itemset with certain item
        k = len(itemset)
        if item[0] in itemset: return False
        for subset in itertools.combinations(itemset, len(itemset) - 1):
            combination = tuple(sorted(list(subset + item)))
            if combination not in self.freq_itemsets[k]: return False
        return True
    
    def generate_candidates(self, k):
        candidates = set()
        for item in self.freq_itemsets[1]:
            for itemset in self.freq_itemsets[k - 1]:
                if self.check_if_viable_combination(itemset, item):
                    candidates.add(tuple(sorted(list(itemset + item))))
        return candidates
    
    def only_freq_itemsets(self, candidates):
        cnt = dict((x, 0) for x in candidates)
        for basket in self.dataset:
            for c in cnt:
                appears = True
                for item in c:
                    if item not in basket: appears = False
                if appears: cnt[c] += 1

        return {itemset for itemset in cnt if cnt[itemset] >= (self.s * self.N)}
        

    def find_k_itemsets(self, k):
        if k < 1: raise Exception('k must be greater than 0.')
        if k == 1: return self.find_freq_items()   # As in itemsets of size 1
        
        start = time.time()
        candidates = self.generate_candidates(k)
        end = time.time()
        print(f'Generated candidates of {k}-itemsets in {end - start}s.')
        
        start = time.time()
        self.freq_itemsets[k] = self.only_freq_itemsets(candidates)
        end = time.time()
        print(f'Found frequent among candidates of {k}-itemsets in {end - start}s.')

        return len(self.freq_itemsets[k]) > 0
    
    def find_all_frequent_itemsets(self):
        k = 0
        done = False
        while not done:
            print(f'Found frequent {k}-itemsets')
            k += 1
            done = not self.find_k_itemsets(k)
        print(f'Size of last found frequent itemset: {k - 1}')
        return k - 1
        

        
        





