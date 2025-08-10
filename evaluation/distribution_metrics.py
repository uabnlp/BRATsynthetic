# Python 3.10 Counters treat empty values as zero
from scipy.spatial import distance
from math import log2
from collections import Counter
import numpy as np


def dictionary_to_normalized_distribution(dictionary, p_name, q_name, eps=1e-12, key_order=None):
    """
    Turn two dicts of counts into aligned probability vectors (sum to 1).
    Returns (p_vec, q_vec, keys).
    """
    p_dict = dictionary[p_name]
    q_dict = dictionary[q_name]
    # Use a stable, deterministic key order
    keys = key_order or sorted(set(p_dict.keys()) | set(q_dict.keys()))
    p = np.array([p_dict.get(k, 0.0) for k in keys], dtype=float)
    q = np.array([q_dict.get(k, 0.0) for k in keys], dtype=float)
    # Smoothing to avoid zeros
    if eps:
        p = p + eps
        q = q + eps
    # Global normalization (not per-coordinate)
    p = p / p.sum()
    q = q / q.sum()
    return p, q, keys


def report_divergences(p, q, *, base=2, print_scipy=False, eps=1e-12):
    """
    Print (and return) divergence metrics in a consistent way.
    By default prints **only** JS divergence.
    - base=2 -> bits; base=e -> nats
    - set print_scipy=True to also print sqrt(JS) from scipy (for cross-checks)
    Returns: {"js": <float>}
    """
    p = np.asarray(p, float); p = np.clip(p, eps, None); p /= p.sum()
    q = np.asarray(q, float); q = np.clip(q, eps, None); q /= q.sum()
    js = js_divergence(p, q, eps=eps, base=base)
    unit = "bits" if base == 2 else "nats"
    print(f"JS Divergence [{unit}]: {js}")
    if print_scipy:
        js_sqrt = distance.jensenshannon(p, q, base=base)  # sqrt(JS)
        print(f"√JS (scipy) [{unit}]: {js_sqrt}")
    return {"js": float(js)}



def kl_divergence_smooth(p, q, eps=1e-12):
    """
    KL(P||Q) with safety: clips, renormalizes, and uses natural log.
    """
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    # Ensure valid distributions
    p = np.clip(p, eps, None); p = p / p.sum()
    q = np.clip(q, eps, None); q = q / q.sum()
    return float(np.sum(p * np.log(p / q)))


def js_divergence(p, q, eps=1e-12, base=2):
    p = np.asarray(p, float)
    q = np.asarray(q, float)
    p = np.clip(p, eps, None); p /= p.sum()
    q = np.clip(q, eps, None); q /= q.sum()
    m = 0.5 * (p + q)
    log_fn = np.log2 if base == 2 else np.log  # bits or nats
    return 0.5 * (np.sum(p * log_fn(p / m)) + np.sum(q * log_fn(q / m)))


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
    print("\nKL Divergence (with smoothing)")
    print(kl_divergence_smooth(distribution1[0], distribution1[1]))
    print("\nJS Divergence")
    print(js_divergence(distribution1[0], distribution1[1]))
    report_divergences(distribution1[0],distribution1[1])

if __name__ == "__main__":
    test()
