
# document being a long string 
def shingle(document, k=10):
    result = set()

    words = document.split()
    for i in range(len(words) - k + 1):
        shingle = words[i:(i+k)]
        #lists are mutable hence not hashable which is why we have to create a single string to hash
        shingle_string = ''.join(shingle)
        result.add(hash(shingle_string))

    return result

#computes the Jaccard similarity of two shingled documents
def compareSets(set1: set, set2: set):
    union = set.union(set1, set2)
    intersection = set.intersection(set1, set2)
    return len(intersection) / len(union)
