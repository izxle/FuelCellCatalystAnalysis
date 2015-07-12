import numpy as np
from arraytoexcel import toClipboardForExcel
import matplotlib.pyplot as plt

def H(cycle, C_lower=0.4, C_upper=0.6):
    # unzip data
    potential = cycle[:,0]
    current = cycle[:,1]
    # cut for anodic sweep
    #TODO: auto calc treshold
    rangPos = (np.diff(potential) >= 0)
    potential = potential[rangPos]
    current = current[rangPos]
    # cut for baseline
    rangC = (potential > C_lower) & (potential < C_upper)
    m, b = np.polyfit(potential[rangC], current[rangC], 1)
    # cut for H-ads
    rangH = (potential < C_lower) & (current > 0.0)    
    xH = potential[rangH]
    yH = current[rangH]
    # substract baseline
    baseline = m * xH + b
    yH -= baseline
    #TODO: add H-desorption area
    # return xyH, baseline
    return xH, yH, baseline

def plot(cycle, xH, yH, y_base, first=None, graph=True, exe=True):
    plt.figure()
    plt.title("CV")
    plt.plot(*zip(*cycle), label="last")
    if first: 
        plt.plot(*zip(*cycle), label="first")
    plt.legend(title="Cycle")
    if "H" in exe:
        plt.plot(xH, y_base, label="H-ads base line")    
        if graph > 1:
            plt.figure()
            plt.plot(xH, yH)
            plt.title("CV-H")
            plt.xlabel('Potencial (V)')
            plt.ylabel('Corriente (A)')
    plt.show()
    
def copy2excel(cycle, first=False):
    toClipboardForExcel(cycle)
    raw_input("copy last cycle CV...")
    print '... done'
    if first:
        toClipboardForExcel(first)
        raw_input("copy first cycle CV...")
        print '... done'

def run(cycle, sr=50.0, C_lower=0.4, C_upper=0.6, first=None,
        exe=True, graph=False, copy=False):
    #INIT data
    xH_pos = None
    yH_pos = None
    y_base = None
    ECSA = None
    #RUN stuff
    if copy:
        copy2excel(cycle, first)
    if "H" in exe:
        xH_pos, yH_pos, y_base = H(cycle, C_lower, C_upper)
        ECSA = np.trapz(yH_pos, xH_pos)/(195.e-6*sr*1.e-3) #cm2
    if graph:
        plot(cycle, xH_pos, yH_pos, y_base, first, graph, exe)
    return ECSA