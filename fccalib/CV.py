import matplotlib.pyplot as plt
import numpy as np

from fccalib.arraytoexcel import toClipboardForExcel


def H(cycle, c_range=(0.4, 0.6)):
    c_lower, c_upper = c_range
    # unzip data
    potential, current = cycle
    # cut for anodic sweep
    #TODO: auto calc treshold
    rangPos = np.diff(potential) >= 0
    potential = potential[1:][rangPos]
    current = current[1:][rangPos]
    # cut for baseline
    rangC = (potential > c_lower) & (potential < c_upper)
    m, b = np.polyfit(potential[rangC], current[rangC], 1)
    # cut for H-ads
    rangH = (potential < c_lower) & (current > 0.0)
    xH = potential[rangH]
    yH = current[rangH]
    # substract baseline
    baseline = m * xH + b
    yH -= baseline
    # TODO: add H-desorption area
    # return xyH, baseline
    return xH, yH, baseline


def plot(cycle_CV, cycle_H, y_base, first=None, graph=True, exe: str = ''):
    potential, current = cycle_CV

    plt.figure('CV')
    plt.title('CV')
    plt.xlabel('Potential [V$_{NHE}$]')
    plt.ylabel('Current [A]')

    plt.plot(potential, current, label="Last")

    # TODO: change units for clarity
    if (first is not None) and (first is not False):
        potential_first, current_first = first
        plt.plot(potential_first, current_first, label='First')
        plt.legend(title="Cycle", loc=0)
    if "H" in exe:
        xH, yH = cycle_H
        plt.plot(xH, y_base, label="H-ads base line")
        if graph > 1:
            plt.figure('CV - H_ads peak')
            plt.plot(xH, yH)
            plt.title("CV-$H_{ads}$")
            plt.xlabel('Potential [V$_{NHE}$]')
            plt.ylabel('Current [A]')
    # plt.show()


def copy2excel(cycle, first=False):
    toClipboardForExcel(cycle)
    input("copy last cycle CV...")
    print('... done')
    if (first is not None) and (first is not False):
        toClipboardForExcel(first)
        input("copy first cycle CV...")
        print('... done')


def run(data, sweep_rate=50.0, c_range=(0.4, 0.6), first=None,
        exe='', graph=False, copy=False):
    # INIT data
    xH_pos = None
    yH_pos = None
    y_base = None
    ECSA = None
    cycle = data.get_scan(-1)
    if first:
        first = data.get_scan(1)
    # RUN stuff
    if copy:
        copy2excel(cycle, first)
    if "H" in exe:
        xH_pos, yH_pos, y_base = H(cycle, c_range)
        if data.sweep_rate:
            sr = data.sweep_rate
        else:
            sr = sweep_rate
        ECSA = np.trapz(yH_pos, xH_pos) / (195.e-6 * sr * 1.e-3)  # cm2
    if graph:
        plot(cycle, (xH_pos, yH_pos), y_base, first, graph, exe)
    return ECSA
