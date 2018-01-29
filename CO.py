import matplotlib.pyplot as plt
import numpy as np

from arraytoexcel import toClipboardForExcel


# TODO: decorate plt.plot to allow xy arrays

def CO(first, second, C_lower=0.4, C_upper=0.6,
       CO_lower=0.6, CO_upper=.9, baseline=True, copy=False):
    """
    cycle: cycles dict {scan, array(data)}
    sr: sweep rate [mV/s]
    C_lower: range lower Carbon capacitance
    C_upper: range upper Carbon capacitance
    """
    # separate x, y
    potential_raw = first[:, 0]
    # substract 2 from 1
    # PATCH, in some files first and second diff size by 1 point
    try:
        current_raw = first[:, 1] - second[:, 1]
    except ValueError:
        try:
            current_raw = first[1:, 1] - second[:, 1]
        except ValueError:
            current_raw = first[:, 1] - second[1:, 1]
    # cut
    # TODO: auto calc treshold
    rangPos = (np.diff(potential_raw) >= 0)
    potential = potential_raw[1:][rangPos]
    current = current_pos = current_raw[1:][rangPos]
    # cut background noise
    rangC_lower = (potential > C_lower) & (potential < C_upper)
    rangC_upper = (potential > CO_upper)
    potential_C = np.concatenate((potential[rangC_lower],
                                  potential[rangC_upper]))
    current_C = np.concatenate((current[rangC_lower],
                                current[rangC_upper]))
    # get baseline eq
    if baseline:
        m, b = np.polyfit(potential_C, current_C, 1)
    # get CO peak
    # TODO: auto calc treshold
    rangCO = (potential > CO_lower) & (potential < CO_upper)
    xCO = potential[rangCO]
    yCO = current[rangCO]
    # substract baseline
    if baseline:
        base_raw = m * potential[rangCO] + b
        yCO -= base_raw
    else:
        base_raw = np.zeros(len(potential_C))

    # generate baseline + second cycle
    # TODO: tidy up
    x2 = second[:, 0]
    y2 = second[:, 1]
    rang2pos = (np.diff(x2) >= 0)
    x2 = x2[1:][rang2pos]
    y2 = y2[1:][rang2pos]
    rang2CO = (x2 > CO_lower) & (x2 < CO_upper)
    x2 = x2[rang2CO]
    y2 = y2[rang2CO]
    # TODO: fix, base_raw & y2 not the same lenght
    # base = base_raw + y2

    # copy to excel
    if copy:
        toClipboardForExcel(first)
        eval(input("copy CO 1..."))
        print('... done')
        toClipboardForExcel(second)
        eval(input("copy CO 2..."))
        print('... done')
        if copy > 1:
            toClipboardForExcel(np.column_stack((potential, current)))
            eval(input("copy CO (1 - 2)..."))
            print('... done')
            # return xyCO, base_rawCO, baseCO
    return (xCO, yCO), (xCO, base_raw)  # , (xCO, base)


def H(first, second, C_lower, copy=False):
    # separate x, y
    potential_raw = first[:, 0]
    # substract 1 from 2
    # PATCH, in some files first and second diff size by 1 point
    try:
        current_raw = second[:, 1] - first[:, 1]
    except ValueError:
        try:
            current_raw = second[1:, 1] - first[:, 1]
        except ValueError:
            current_raw = second[:, 1] - first[1:, 1]
    # cut for anodic sweep
    # TODO: auto calc treshold
    rangPos = (np.diff(potential_raw) >= 0)
    potential = potential_raw[1:][rangPos]
    current = current_pos = current_raw[1:][rangPos]
    # cut for H region
    rangH = (potential < C_lower)
    potential = potential[rangH]
    current = current[rangH]
    # return xyH
    return (potential, current)


def plot(first, second, paramsCO, paramsH, exe, graph):
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
        if "H" in exe:
            xyH = paramsH
            if graph > 2:
                plt.figure(r'CO - normalized $H_{ads}$ peak')
                # treated data
                x, y = xyH
                plt.plot(x, y)
                plt.title("H-ads peak")
    plt.figure()
    plt.plot(*list(zip(*first)), color='b', linestyle=':', label='1')
    plt.plot(*list(zip(*second)), color='g', linestyle=':', label='2')
    plt.title("CO")
    plt.legend(title='Cycle', loc=0)
    if graph > 1:
        # TODO: plot baselines into raw data
        # TODO: fill integrated area
        pass
    # plt.show()


def run(first, second, sr=20.,
        C_lower=0.4, C_upper=0.6, CO_lower=0.6, CO_upper=.9,
        exe=True, graph=True, baseline=True, copy=False):
    # INIT data
    params = {}
    ECSA_CO = None
    ECSA_H = None
    # RUN stuff
    if "CO" in exe or exe is True:
        params["CO"] = CO(first, second, C_lower, C_upper,
                          CO_lower, CO_upper, baseline=baseline, copy=copy)
        x, y = params["CO"][0]
        ECSA_CO = np.trapz(y, x) / (210.e-6 * sr * 1.e-3)  # cm2
    if "H" in exe:
        params["H"] = H(first, second, C_lower, copy)
        x, y = params["H"]
        ECSA_H = np.trapz(y, x) / (420.e-6 * sr * 1.e-3)  # cm2
    if graph:
        plot(first, second, paramsCO=params.get("CO"),
             paramsH=params.get("H"), exe=exe, graph=graph)

    return ECSA_CO, ECSA_H


if __name__ == "__main__":
    pass
else:
    pass
    # del trapz
    # del plt
    # del np
    # del interp1d
