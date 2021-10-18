import numpy as np
from matplotlib import pyplot as plt
import random


def get_cur_val(val, prev, stddev, percentile):
    if val < prev:
        return prev - stddev / percentile
    elif val > prev:
        return prev + stddev / (1 - percentile)
    else:
        return val


def moving_precentile(vals, percentile=0.99, ratio=0.005, momentum1=0.999, momentum2=0.999):
    running_percentiles = []
    running_means = []
    running_var = 0
    for v in vals:
        running_var = momentum1 * running_var + (1 - momentum1) * v * v
        stddev = running_var ** 0.5
        if not running_percentiles:
            running_percentiles.append(v)
            running_means.append(v)
        else:
            running_percentiles.append(get_cur_val(v, running_percentiles[-1], stddev * ratio, percentile))
            running_means.append(momentum2 * running_means[-1] + (1 - momentum2) * running_percentiles[-1])

    plt.plot(running_percentiles, label='mp:momentum1=%.4f,percentile=%.4f,ratio=%.6f' % (momentum1, percentile, ratio))
    plt.plot(running_means, label='mpa:momentum1=%.4f,percentile=%.4f,ratio=%.6f' % (momentum1, percentile, ratio))
    print(sum(running_percentiles) / len(running_percentiles), sum(running_means) / len(running_means))


if __name__ == '__main__':
    # moving_average()
    vals = [random.random() for _ in range(100000)]
    moving_precentile(vals, 0.8, 0.01)
    moving_precentile(vals, 0.99, 0.01)
    # moving_precentile(vals, 0.5, 0.001)
    # moving_precentile(vals, 0.5, 0.0001)
    plt.legend()
    plt.show()