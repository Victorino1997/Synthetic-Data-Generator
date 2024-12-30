import numpy as np


def _rand_bool(true_prob):
    return np.random.choice([True, False], p=[true_prob, 1 - true_prob])
