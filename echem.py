import numpy as np

from reader import Data


# def manage_mask_range(f):
#     def wrapper(x, y, start=None, end=None, mask=None, **kwargs):
#         if mask is None:
#             mask = np.ones(len(x), dtype=bool)
#             if start:
#                 mask &= (start <= x)
#             if end:
#                 mask &= (x <= end)
#         return f(x, y, mask=mask, **kwargs)
#     return wrapper
#
#
# def check_inputs(arg_list=[], type_list=[], linear=[], numbers=[], **kw):
#     def decorator(f):
#         def wrapper(*args, **kwargs):
#             if len(arg_list) != len(type_list):
#                 raise ValueError(f'arg_list <{len(arg_list)}> and type_list '
#                                  f'<{len(type_list)}> must have same length')
#
#             for name, t, arg in zip(arg_list, type_list, args):
#                 if t == 'linear' and len(arg.shape) != 1:
#                     raise ValueError(f'{name} is not a 1-d array')
#             for name in linear:
#                 arg = kw[name]
#                 if len(arg.shape) != 1:
#                     raise ValueError(f'{name} is not a 1-d array')
#
#             return f(*args, **kwargs)
#         return wrapper
#     return decorator


def chronoamp_ECSA(data: Data, mass: float = 0) -> float:
    x = data.get_time()
    y = data.get_current()

    baseline = calc_baseline(x, y, start=50, end=200)

    charge = integrate_peak(x, y, start=0, end=50, baseline=baseline)
    # TODO: integrate with electrode object
    # get factor and mass info from electrode
    factor = 210e-6 * 1e4  # (C / cm^2) * (cm^2 / m^2) = C / m^2
    area = charge / factor
    if mass:
        area /= mass
    # m^2_Pt / g_Pt
    return area


def calc_baseline(x: np.ndarray, y: np.ndarray, mask: np.ndarray = None,
                  start: float = None, end: float = None) -> np.ndarray:
    assert len(x.shape) == 1, f'x is not a 1-d array'
    assert len(y.shape) == 1, f'y is not a 1-d array'
    assert len(x) == len(y), f'x <{len(x)}> and y <{len(y)}> must have the same length'

    mask = manage_mask_range(x, y, start, end, mask)

    m, b = np.polyfit(x[mask], y[mask], 1)
    baseline = m * x + b

    return baseline


def integrate_peak(x: np.ndarray, y: np.ndarray, mask: np.ndarray = None,
                   start: float = None, end: float = None,
                   baseline: np.ndarray = None) -> float:
    """
    Integrate area
    :param x:
    :param y:
    :param start: lower limit in x of peak to be integrated
    :param end: upper limit in x of peak to be integrated
    :param mask:
    :param baseline:
    :return:
    """
    assert len(x.shape) == 1, f'x is not a 1-d array'
    assert len(y.shape) == 1, f'y is not a 1-d array'
    assert len(x) == len(y), f'x <{len(x)}> and y <{len(y)}> must have the same length'

    if baseline is not None:
        assert len(baseline.shape) == 1, f'baseline is not a 1-d array'
    else:
        baseline = np.zeros(len(y))

    mask = manage_mask_range(x, y, start, end, mask)

    x = x[mask]
    y = y[mask] - baseline[mask]

    area = np.trapz(x, y)
    return area


def manage_mask_range(x, y, start, end, mask):
    if mask is None:
        mask = np.ones(len(x), dtype=bool)
        if start:
            mask &= (start <= x)
        if end:
            mask &= (x <= end)
    return mask
