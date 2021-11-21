import itertools
import time
import multiprocessing

#counts all basket where c is a subset - used for multiprocessing
def count_support(c, baskets):
    counter = 0
    for basket in baskets:
        appears = True
        for item in c:
            if item not in basket: 
                appears = False
                break
        if appears: counter += 1
    return (c, counter)

class AssociationRulesFinder:
    # freq_itemsets is a dictionary containing the itemset + the support
    def __init__(self, freq_itemsets):
        self.freq_itemsets = freq_itemsets

    def getAssociationRules(self, c):
        result = list()
        for itemset in self.freq_itemsets:
            for m in range(1, len(itemset)):
                for subset in itertools.combinations(itemset, m):
                    if self.freq_itemsets[itemset] / self.freq_itemsets[subset] > c:
                        result.append((set(subset), set(itemset).difference(set(subset))))
        return result


#ITEMSETS ARE TREATED AS TUPLES!
class FrequentItemsetFinder:
    def __init__(self, dataset, s):
        self.freq_itemsets = dict() # 1: set(frequent items), 2: set(frequent pairs)...
        self.dataset = dataset      # List of iterables, each iterable represents one basket
        self.s = s                  # Support threshold
        self.N = len(self.dataset)

    # The first step is to find frequent items, which is different from other steps because we have to look at all items
    def find_freq_items(self):
        cnt = dict()
        for basket in self.dataset:
            for item in basket:
                if item not in cnt: cnt[item] = 0
                cnt[item] += 1

        # Keep only items with relative support s
        self.freq_itemsets[1] = {(item,) for item in cnt if cnt[item] >= (self.s * self.N)}
        return len(self.freq_itemsets[1]) > 0
    
    # Check if it makes sense to expand an itemset with certain item
    def check_if_viable_combination(self, itemset, item):          
        k = len(itemset)
        if item[0] in itemset: return False     # There's no point in expanding an itemset with an element already present
        for m in range(1, k):       # All subsets of the original itemset
            for subset in itertools.combinations(itemset, m):  # Because all subsets have at least the same support as their super sets
                combination = tuple(sorted(list(subset + item)))   # this conditions gets rid of all combinations which we know can't be frequent because we have concluded that one of its subsets is unfrequent in the previous pass 
                if combination not in self.freq_itemsets[m+1]: return False     
        return True                                                        
    
    # Generate candidate itemsets which might be frequent (all of their subsets are frequent)
    def generate_candidates(self, k):
        candidates = set()
        for item in self.freq_itemsets[1]:
            for itemset in self.freq_itemsets[k - 1]:
                if self.check_if_viable_combination(itemset, item):
                    candidates.add(tuple(sorted(list(itemset + item))))
        return candidates
    
    # Keep only the candidates that have support at least s * size of dataset
    def only_freq_itemsets(self, candidates):
        cnt = dict((x, 0) for x in candidates)

        # we had big performance issues, therefore we use multiprocessing to speed everything up
        pool = multiprocessing.Pool()
        counter = pool.starmap(count_support, zip(cnt, itertools.repeat(self.dataset)))

        thresh = self.s * self.N
        return {c[0] for c in counter if c[1] >= thresh}
        
    # Find all frequent itemsets of size k
    def find_k_itemsets(self, k):
        if k < 1: raise Exception('k must be greater than 0.')
        if k == 1: return self.find_freq_items()   # As in itemsets of size 1
        
        candidates = self.generate_candidates(k)
        self.freq_itemsets[k] = self.only_freq_itemsets(candidates)

        return len(self.freq_itemsets[k]) > 0  # If none such itemsets exist return False
    
    # starting at k=1 find all frequent k-itemsets
    def find_all_frequent_itemsets(self):
        k = 0
        done = False
        elapsed_time = 0
        while not done:  # Stop searching when there are no such itemsets for the current k
            k += 1
            start = time.time()
            done = not self.find_k_itemsets(k)
            end = time.time()
            print(f'[FIFinder]: Found frequent {k}-itemsets in {end - start}s of size {len(self.freq_itemsets[k])}.')         # Print some time info
            elapsed_time += end - start
        print(f'[FIFinder]: Found all frequent itemsets with support threshold {self.s}% in {elapsed_time}s.')
        return k - 1, elapsed_time     # Return last frequent k-itemsets found

    # returns the frequent itemsets together with the absolute count
    def getFreqItemsetsWithSupport(self):
        counts = dict()
        for itemsets in self.freq_itemsets.values():
            pool = multiprocessing.Pool()
            counter = pool.starmap(count_support, zip(itemsets, itertools.repeat(self.dataset)))
            for count in counter:
                counts[count[0]] = count[1]
        return counts
    