from FrequentItemsetFinder import FrequentItemsetFinder

baskets = None
with open('T10I4D100K.dat', 'r') as f:
    baskets = [set(l.split()) for l in f.readlines()]
s = 0.01
print(f's={s}')
finder = FrequentItemsetFinder(baskets, s)
finder.find_all_frequent_itemsets()
for i in range(len(finder.freq_itemsets)):
    k = i + 1
    print(f'\nFREQUENT ITEMSETS OF SIZE {k}')
    for itset in finder.freq_itemsets[k]:
        print(f'    {itset}')
    print()
    