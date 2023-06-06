# Python 3.10 Counters treat empty values as zero
from scipy.spatial import distance
from math import log2
from collections import Counter


# Standard KL divergence
def kl_divergence(p, q):
    return sum(p[i] * log2(p[i] / q[i]) for i in range(len(p)))


# LaPlace +1 Smoothing Divergence
def kl_divergence_smooth(p, q):
    return sum(p[i] * log2((p[i] + 1) / (q[i] + 1)) for i in range(len(p)))


def dictionary_to_normalized_distribution(dictionary, distribution_p_name, distribution_q_name, normalized_dist):
    distribution_p = dictionary[distribution_p_name]
    distribution_q = dictionary[distribution_q_name]
    normalized_dist = distributions_to_list(distribution_p, distribution_q, normalized_dist)
    return normalized_dist


def distributions_to_list(distribution_p, distribution_q, distribution_lists):
    for column in distribution_q.keys():
        total = distribution_p[column] + distribution_q[column]
        distribution_lists[0].append(distribution_p[column] / total)
        distribution_lists[1].append(distribution_q[column] / total)
    return distribution_lists


def norm_counter_values(k, v, tot):
    norm = v / tot[k]
    return norm


# Converts 2 Counter objects into a normalized distribution
def counter2distribution(a, b):
    totals = Counter(a + b)
    # Missing Values Replaced
    for key in totals:
        a.setdefault(key, 0.0)
        b.setdefault(key, 0.0)
    p = {k: norm_counter_values(k, v, totals) for (k, v) in a.items()}
    q = {k: norm_counter_values(k, v, totals) for (k, v) in b.items()}
    return list((dict(sorted(p.items()))).values()), list((dict(sorted(q.items()))).values())


def counters_to_jensenshannon(a, b):
    dists = counter2distribution(a.copy(), b.copy())
    return distance.jensenshannon(dists[0], dists[1])


# TEST
def test():
    p1 = {'p1': 2.0, 'B': 3.0, 'C': 4.0}
    p2 = {'B': 3.0, 'C': 2.0, 'D': 1.0}
    a = Counter(p1)
    b = Counter(p2)
    print("P: " + str(a))
    print("Q: " + str(b))

    distribution1 = counter2distribution(a, b)
    print("Distributions")
    print(distribution1)
    print("Jensen-Shannon Symetric Measure")
    print(distance.jensenshannon(distribution1[0], distribution1[1]))
    print("\nKL Divergence (with LaPlace smoothing)")
    print(kl_divergence_smooth(distribution1[0], distribution1[1]))

    print("\nKL Divergence (no LaPlace smoothing)")
    p3 = {'A': 2, 'B': 3, 'C': 4}
    p4 = {'A': 3, 'B': 2, 'C': 1}
    distribution2 = counter2distribution(Counter(p3), Counter(p4))
    print(distribution2)
    print(kl_divergence(distribution2[0], distribution2[1]))

    print("\nKL Divergence2 (no LaPlace smoothing)")
    mydict = {"foo": Counter(p3), "bar": Counter(p4)}
    distributions = dictionary_to_normalized_distribution(mydict, "foo", "bar", ([], []))
    print(kl_divergence(distributions[0], distributions[1]))

