#TODO: quitar lin base dl CO
from arraytoexcel import toClipboardForExcel
from scipy.integrate import trapz
#from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np

def run(cycle, sr=20., rCl=0.4, rCu=0.6, rCOl=0.6, rCOu=.9, graph=True, addH=True, copy=False):
    """
    cycle: cycles dict {scan, array(data)}
    sr: sweep rate [mV/s]
    rCl: range lower Carbon capacitance
    rCu: range upper Carbon capacitance
    graph: 0[-], 1[CO], <1[CO+H]
    addH: 0[CO], 1[CO+H], <1[H]
    """
    #in case only H from CV
    if addH>1:
        #separate x, y
        x = cycle[1][:,0]
        y = cycle[1][:,1]
        #cut
        #TODO: auto cut
        rang = (np.diff(x)>=0)
        x = x[rang]
        y = y[rang]
        #calc
        #vvvvvvvvvvvvvvv
        #TODO: calc lims
        #^^^^^^^^^^^^^^^
        rangH = (x<rCl)
        rangC = (x>rCl)&(x<rCu)
        x = x[rangH]
        y = y[rangH] - np.average(y[rangC])
        #ElectoChemical Surface Area
        ECSA = trapz(y, x)/(210.e-6*sr*1.e-3) #cm2
        #plot
        if graph:
            plt.figure()
            plt.plot(x, y)
            plt.title("CO-H")
            plt.xlabel('Potencial (V)')
            plt.ylabel('Corriente (A)')
        if graph>1:
            pass
        return ECSA
    #separate x, y
    x = cycle[1][:,0]
    #patch, in OLD cycles diff size
    try:
        y = cycle[1][:,1] - cycle[2][:,1]
    except ValueError:
        try:
            y = cycle[1][1:,1] - cycle[2][:,1]
        except ValueError:
            y = cycle[1][:,1] - cycle[2][1:,1]
    #cut
    #TODO: auto cut
    rang = (np.diff(x)>=0)
    x = x[rang]
    y = y[rang]
    #cut bkgdn noise
    rangCl = (x>rCl)&(x<rCu)
    rangCu = (x>rCOu)
    xx = np.concatenate((x[rangCl], x[rangCu]))
    yy = np.concatenate((y[rangCl], y[rangCu]))    
    m, b = np.polyfit(xx, yy, 1)
    
    rangCO = (x>rCOl)&(x<rCOu)
    yCO = y[rangCO]
    yCO -= m*x[rangCO] + b
    #copy to excel
    if copy:
        toClipboardForExcel(np.column_stack((x, y)))
        raw_input("copy CO profile...")
        print '... done'        
    #plot difference
    #TODO: add grey area
    if graph>1:
        plt.figure()
        if copy:
            toClipboardForExcel(cycle[1])
            raw_input("copy CO 1...")
            print '... done'
            toClipboardForExcel(cycle[2])
            raw_input("copy CO 2...")
            print '... done'
        plt.plot(*zip(*cycle[1]), color='b', linestyle=':')
        plt.plot(*zip(*cycle[2]), color='g', linestyle=':')
        plt.plot(x, y)
        plt.plot(x[(x>rCu)&(x<rCOu)], x[(x>rCu)&(x<rCOu)]*0)
        plt.title("CO")
        plt.legend(['1', "2", 'norm'])
    
    if addH:
        rangH = (x<0.4)&(y<0.0)
        xH = x[rangH]
        yH = y[rangH]*-1.
        
    #ElectoChemical Surface Area
    ECSA = trapz(yCO, x[rangCO])/(2.*210.e-6*sr*1.e-3) #cm2
    #plot limd
    if graph:
        plt.figure()
        plt.plot(x[rangCO], yCO)
        plt.xlabel('Potencial (V)')
        plt.title("CO-peak")
        plt.ylabel('Corriente (A)')
        if addH:
            plt.figure()
            plt.title("CO-H")
            plt.plot(xH,yH)
        plt.show()
    if addH:
        aH = trapz(yH, xH)/(210.e-6*sr*1.e-3) #cm2
        return ECSA, aH
    else:
        return ECSA

def H(cycle, sr=20., graph=True):
    
    return

#0.6 a 1

if __name__=="__main__":
    pass
else:
    pass
    #del trapz
    #del plt
    #del np
    #del interp1d