# Python 3.10 Counters treat empty values as zero
import collections
from scipy.spatial import distance
from math import log2
from collections import Counter

def KL_divergence(p, q):
    return sum(p[key] * log2(p[key] / q[key]) for key in p)

# LaPlace +1 Smoothing Divergence
def kl_divergence(p, q):
 return sum(p[i] * log2((p[i]+1)/(q[i]+1)) for i in range(len(p)))


def norm_counter_values(k,v,tot):
    norm = v/tot[k]
    return norm


# Converts 2 Counter objects into a normalized distribution
def counter2distribution(a, b):
    totals = Counter(a + b)
    #Missing Values Replaced
    for key in totals:
        a.setdefault(key,0.0)
        b.setdefault(key,0.0)
    p = {k:norm_counter_values(k,v,totals) for (k,v) in a.items()}
    q = {k:norm_counter_values(k,v,totals) for (k,v) in b.items()}
    P = list((dict(sorted(p.items()))).values())
    Q = list((dict(sorted(q.items()))).values())
    return(P,Q)


def counters_to_jensenshannon(a,b):
    dists = counter2distribution(a.copy(),b.copy())
    return distance.jensenshannon(dists[0],dists[1])


# TEST
def test():
    A = { 'A':2.0,'B':3.0, 'C':4.0 }
    B = { 'B':3.0, 'C':2.0, 'D':1.0 }
    a = Counter(A)
    b = Counter(B)
    print("P: "+str(a))
    print("Q: "+str(b))

    dists = counter2distribution(a,b)
    print("Distributions")
    print(dists)
    print("Jensen-Shannon Symetric Measure")
    print(distance.jensenshannon(dists[0],dists[1]))
    print("KL Divergence (with LaPlace smoothing)")
    print(kl_divergence(dists[0],dists[1]))

