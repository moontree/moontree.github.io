import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

mean_hunger = 5
samples_per_day = 100
n_days = 10000
samples = np.random.normal(loc=mean_hunger, size=(n_days, samples_per_day))
daily_maxes = np.max(samples, axis=1)


def gumbel_dist(mean, stddev):
    x = np.arange(-5, 20, 0.01)
    z = (x - mean) / stddev
    y = np.exp(-(z + np.exp(-z)))
    plt.plot(x, y, label='mean: %f, stddev: %f' % (mean, stddev))


def gumbel_dist_plot():
    gumbel_dist(0, 1.0)
    gumbel_dist(1.0, 1.0)
    gumbel_dist(1.0, 2.0)
    gumbel_dist(2.0, 3.0)
    plt.legend(loc=1)
    plt.show()


def gumbel_max_tric():
    n_cats = 7
    cats = np.arange(n_cats)
    probs = np.random.randint(low=1, high=20, size=n_cats)
    probs = probs / sum(probs)
    logits = np.log(probs)

    plt.bar(cats, probs)
    plt.xlabel("Category")
    plt.ylabel("Probability")
    plt.show()

if __name__ == '__main__':
    # gumbel_dist_plot()
    gumbel_max_tric()