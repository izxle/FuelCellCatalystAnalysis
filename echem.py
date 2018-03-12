import numpy as np

from reader import Data


def chronoamperometry(data: Data, ):
    x = data.get_time()
    y = data.get_current()

    return


def integrate_peak(x, y, xrange=None, mask=None):
    if mask is None and xrange is not None:
        start, end = xrange
        mask = (start <= x) & (x < end)

    x = x[mask]
    y = y[mask]

    res = np.trapz(x, y)
    return res
