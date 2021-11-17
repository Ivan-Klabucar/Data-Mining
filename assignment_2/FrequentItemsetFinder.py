import itertools
import time


#ITEMSETS ARE TREATED AS TUPLES!
class FrequentItemsetFinder:
    def __init__(self, dataset, s):
        self.freq_itemsets = dict() # 1: set(frequent items), 2: set(frequent pairs)...
        self.dataset = dataset      # List of iterables, each iterable represents one basket
        self.s = s                  # Support threshold
        self.N = len(self.dataset)

    # The first step is to find frequent items, which is different from other steps because we have to look at all items
    def find_freq_items(self):      # There's no duplicates in baskets I checked.
        cnt = dict()
        for basket in self.dataset:
            for item in basket:
                if item not in cnt: cnt[item] = 0
                cnt[item] += 1

        self.freq_itemsets[1] = {(item,) for item in cnt if cnt[item] >= (self.s * self.N)}  # Keep only items with relative support s
        return len(self.freq_itemsets[1]) > 0
    
    def check_if_viable_combination(self, itemset, item):          # Check if it makes sense to expand an itemset with certain item
        k = len(itemset)
        if item[0] in itemset: return False                        # There's no point in expanding an itemset with an element already present
        for subset in itertools.combinations(itemset, len(itemset) - 1):  # All subsets of the original itemset but with one item removed
            combination = tuple(sorted(list(subset + item)))              
            if combination not in self.freq_itemsets[k]: return False     # Because all subsets have at least the same support as their super sets
        return True                                                       # this conditions gets rid of all combinations which we know can't be frequent because we have concluded that one of its subsets is unfrequent in the previous pass
    
    def generate_candidates(self, k):                                     # Generate candidate itemsets which might be frequent (all of their subsets are frequent)
        candidates = set()
        for item in self.freq_itemsets[1]:
            for itemset in self.freq_itemsets[k - 1]:
                if self.check_if_viable_combination(itemset, item):
                    candidates.add(tuple(sorted(list(itemset + item))))
        return candidates
    
    def only_freq_itemsets(self, candidates):                             # Keep only the candidates that have support at least s * size of dataset
        cnt = dict((x, 0) for x in candidates)
        for basket in self.dataset:
            for c in cnt:
                appears = True
                for item in c:
                    if item not in basket: appears = False
                if appears: cnt[c] += 1

        return {itemset for itemset in cnt if cnt[itemset] >= (self.s * self.N)}
        

    def find_k_itemsets(self, k):                                 # Find all frequent itemsets of size k
        if k < 1: raise Exception('k must be greater than 0.')
        if k == 1: return self.find_freq_items()   # As in itemsets of size 1
        
        candidates = self.generate_candidates(k)
        self.freq_itemsets[k] = self.only_freq_itemsets(candidates)

        return len(self.freq_itemsets[k]) > 0                    # If none such itemsets exist return False
    
    def find_all_frequent_itemsets(self):       # starting at k=1 find all frequent k-itemsets
        k = 0
        done = False
        elapsed_time = 0
        while not done:                         # Stop searching when there are no such itemsets for the current k
            k += 1
            start = time.time()
            done = not self.find_k_itemsets(k)
            end = time.time()
            print(f'[FIFinder]: Found frequent {k}-itemsets in {end - start}s.')         # Print some time info
            elapsed_time += end - start
        print(f'[FIFinder]: Found all frequent itemsets with support threshold {self.s}% in {elapsed_time}s.')
        return k - 1, elapsed_time     # Return last frequent k-itemsets found
        

        
        





