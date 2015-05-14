import numpy as np
from arraytoexcel import toClipboardForExcel
import matplotlib.pyplot as plt

def H(cycle, sr=50.0, rCl=0.4, rCu=0.6, graph=True, copy=False, fCV=None):
    x = cycle[:,0]
    y = cycle[:,1]
    #copy to excel
    if copy:
        toClipboardForExcel(cycle)
        raw_input("copy CV...")
        print '... done'
        if not fCV is None:
            toClipboardForExcel(fCV)
            raw_input("copy fCV...")
            print '... done'
    rang = (np.diff(x)>=0)
    x = x[rang]
    y = y[rang]
    #calc
    #vvvvvvvvvvvvvvv
    #TODO: calc lims
    #^^^^^^^^^^^^^^^
    rangC = (x>rCl)&(x<rCu)
    m, b = np.polyfit(x[rangC], y[rangC], 1)
    #y -= np.average(y[rangC])
    rangH = (x<rCl)&(y>0.0)    
    x = x[rangH]
    y = y[rangH]
    y -= m*x + b
    #ElectoChemical Surface Area
    ECSA = np.trapz(y, x)/(195.e-6*sr*1.e-3) #cm2
    #plot
    if graph>1:
        plt.figure()
        plt.title("CV")
        plt.plot(cycle[:,0], cycle[:,1])
        if not fCV is None: plt.plot(fCV[:,0], fCV[:,1])
    if graph>2:
        plt.plot(x, m*x+b)
    if graph:
        plt.figure()
        plt.plot(x, y)
        plt.title("CV-H")
        plt.xlabel('Potencial (V)')
        plt.ylabel('Corriente (A)')
        plt.show()
    return ECSA