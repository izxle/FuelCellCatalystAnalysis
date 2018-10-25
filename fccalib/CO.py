from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .writer import save_to_excel


# TODO: decorate plt.plot to allow xy arrays

def CO(cycle_CO, cycle_baseline, c_range=(0.4, 0.6), co_range=(0.6, 0.9),
       add_baseline=True, copy=False):
    """
    cycle: cycles dict {scan, array(data)}
    sr: sweep rate [mV/s]
    c_range: range lower Carbon capacitance
    """
    c_lower, c_upper = c_range
    co_lower, co_upper = co_range
    # separate x, y
    potential_raw = cycle_CO[0]
    # substract 2 from 1
    # PATCH, in some files first and second diff size by 1 point
    try:
        current_raw = cycle_CO[1] - cycle_baseline[1]
    except ValueError:
        try:
            current_raw = cycle_CO[1, 1:] - cycle_baseline[1]
        except ValueError:
            current_raw = cycle_CO[1] - cycle_baseline[1, 1:]
    # cut
    # TODO: auto calc threshold
    rangPos = np.diff(potential_raw) >= 0
    potential = potential_raw[1:][rangPos]
    current = current_pos = current_raw[1:][rangPos]
    # cut background noise
    rangC_lower = (potential > c_lower) & (potential < c_upper)
    rangC_upper = (potential > co_upper)
    potential_C = np.concatenate((potential[rangC_lower],
                                  potential[rangC_upper]))
    current_C = np.concatenate((current[rangC_lower],
                                current[rangC_upper]))
    # get baseline eq
    if add_baseline:
        m, b = np.polyfit(potential_C, current_C, 1)
    # get CO peak
    # TODO: auto calc treshold
    rangCO = (potential > co_lower) & (potential < co_upper)
    xCO = potential[rangCO]
    yCO = current[rangCO]
    # substract baseline
    if add_baseline:
        base_raw = m * potential[rangCO] + b
        yCO -= base_raw
    else:
        base_raw = np.zeros(len(potential_C))

    # generate baseline + second cycle
    # TODO: tidy up
    x2 = cycle_baseline[:, 0]
    y2 = cycle_baseline[:, 1]
    rang2pos = (np.diff(x2) >= 0)
    x2 = x2[1:][rang2pos]
    y2 = y2[1:][rang2pos]
    rang2CO = (x2 > co_lower) & (x2 < co_upper)
    x2 = x2[rang2CO]
    y2 = y2[rang2CO]
    # TODO: fix, base_raw & y2 not the same lenght
    # base = base_raw + y2

    # copy to excel
    if copy:
        d = OrderedDict([('potential', cycle_CO[0]),
                         ('cycle CO\ncurrent', cycle_CO[1]),
                         ('baseline\ncurrent', cycle_baseline[1])])
        df = pd.DataFrame(data=d)
        save_to_excel(df, 'results.xlsx', 'CO', index=False)

        d = OrderedDict([('potential', potential),
                         ('CO peak\ncurrent', current)])
        df = pd.DataFrame(data=d)
        save_to_excel(df, 'results.xlsx', 'CO', 5, index=False)

    return (xCO, yCO), (xCO, base_raw)  # , (xCO, base)


def H(cycle_CO, cycle_baseline, c_lower, copy=False):
    # separate x, y
    potential_raw = cycle_CO[0]
    # substract 1 from 2
    # PATCH, in some files first and second diff size by 1 point
    try:
        current_raw = cycle_baseline[1] - cycle_CO[1]
    except ValueError:
        try:
            current_raw = cycle_baseline[1, 1:] - cycle_CO[1]
        except ValueError:
            current_raw = cycle_baseline[1] - cycle_CO[1, 1:]
    # cut for anodic sweep
    # TODO: auto calc threshold
    rangPos = np.diff(potential_raw) >= 0
    potential = potential_raw[1:][rangPos]
    current = current_pos = current_raw[1:][rangPos]
    # cut for H region
    rangH = potential < c_lower
    potential = potential[rangH]
    current = current[rangH]
    # return xyH
    return potential, current


def plot(cycle_CO, cycle_baseline, paramsCO, paramsH, exe, graph):
    """
    TODO: add somethig here
    """
    # TODO: use plt.axes for better structure

    if graph > 1:
        if "CO" in exe:
            xyCO, base_rawCO = paramsCO  # , baseCO = paramsCO
            if graph > 2:
                plt.figure('CO - normalized CO peak')
                # treated data
                x, y = xyCO
                plt.plot(x, y)
                # baseline
                # TODO: add baseline
                plt.title("CO peak")
                plt.xlabel('Potential [V$_{NHE}$]')
                plt.ylabel('Current [A]')

        if "H" in exe:
            xyH = paramsH
            if graph > 2:
                plt.figure('CO - H_ads')
                # treated data
                x, y = xyH
                plt.plot(x, y)
                plt.title("CO stripping - normalized $H_{ads}$ peak")
                plt.xlabel('Potential [V$_{NHE}$]')
                plt.ylabel('Current [A]')

    potential_CO, current_CO = cycle_CO
    potential_baseline, current_baseline = cycle_baseline
    plt.figure('CV - CO stripping')
    plt.plot(potential_CO, current_CO, color='b', linestyle=':', label='First')
    plt.plot(potential_baseline, current_baseline, color='g', linestyle=':', label='Second')
    plt.xlabel('Potential [V$_{NHE}$]')
    plt.ylabel('Current [A]')
    plt.title("CO stripping")
    plt.legend(title='Cycle', loc=0)
    if graph > 1:
        # TODO: plot baselines into raw data
        # TODO: fill integrated area
        pass
    # plt.show()


def run(data, sweep_rate=20.,
        c_range=(0.4, 0.6), co_range=(0.6, 0.9),
        exe='', graph=True, baseline=False, copy=False):
    # INIT data
    params = {}
    area_CO = None
    area_H = None

    cycle_CO = data.get_scan(1)
    cycle_baseline = data.get_scan(2)

    if data.sweep_rate:
        sr = data.sweep_rate
    else:
        sr = sweep_rate

    # RUN stuff
    if "CO" in exe:
        params["CO"] = CO(cycle_CO, cycle_baseline, c_range, co_range, add_baseline=baseline, copy=copy)
        x, y = params["CO"][0]
        Q_CO = np.trapz(y, x)  # V C / s
        factor_CO = 420e-6 * sr  # C V / s cm2
        area_CO = Q_CO / factor_CO  # cm2
    if "H" in exe:
        params["H"] = H(cycle_CO, cycle_baseline, co_range[0], copy)
        x, y = params["H"]
        Q_H = np.trapz(y, x)  # V C / s
        factor_H = 210e-6 * sr * 1.e-3  # C V / s cm2
        area_H = Q_H / factor_H  # cm2
    if graph:
        plot(cycle_CO, cycle_baseline, paramsCO=params.get("CO"),
             paramsH=params.get("H"), exe=exe, graph=graph)

    return area_CO, area_H


if __name__ == "__main__":
    pass
