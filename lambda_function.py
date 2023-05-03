import numpy as np
import scipy.stats as si


def lambda_handler(event, context):
    _normal_distribution(0, 1)


def _normal_distribution(value):
    normal_dist = si.norm.cdf(value, 0.0, 1.0)
    print(normal_dist, 'NORMAL DISTRIBUTION')
    return normal_dist