import matplotlib.pyplot as plt
from pylab import polyfit, poly1d
from numpy import average, diff, log10, column_stack
from arraytoexcel import toClipboardForExcel

#TODO: maybe a var Cycle con props utils

def tafel(cycle, WE=None, base=None, iL_lower=.2, iL_upper=.4,
          par=1.5, sr=20., graph=True, copy=False):
    # unzip data
    potential = cycle[:,0]
    current = cycle[:,1]
    # cut for useful data
    #TODO: auto calc treshold
    rang = (potential > iL_lower)[1:] & (diff(potential) >= 0)
    potential = potential[rang]
    current = current[rang]
    #current to specific density [A/cm2 Pt]
    rrr = (potential > 0.89) & (potential <  0.91)
    aaa = current[rrr] / WE.mCatCen / 1.e-6
    bbb = potential[rrr]
    print column_stack((bbb, aaa))
    #TODO: ECSA
    #current = current/WE.area.big()
    current = current/WE.area.big()
    #get diffusion controled current JL
    #TODO: auto cut
    JLrang = (potential>iL_lower) & (potential<iL_upper)
    JL = average(current[JLrang])
    #correction 2 get Jk, cut apres 0.4 pk ruido
    rang = (potential>iL_upper)
    potential = potential[rang]
    current = current[rang]
    Jk = current*JL / (JL - current)
    #tafel slopes
    logJk = log10(abs(Jk))
    #TODO: calc tafel rangs
    #get points cn pend neg
    negS = diff(logJk)<0
    potential = potential[negS]
    current = current[negS]
    logJk = logJk[negS]
    lowCh = logJk[-1] + par  #####arbitrario TODO: calc
    ##
    lowRang = (logJk>lowCh) & (logJk<lowCh+1)
    highRang = (logJk>lowCh+1) & (logJk<lowCh+2)
    #TOpatch: start ~0.92V
    
    ##
    ##
    #lowRang = (logJk>-4.53) & (logJk<-3.53)
    #highRang = (logJk>-3.53) & (logJk<-2.53)
    lowJk = logJk[lowRang]
    highJk = logJk[highRang]
    lowfit = polyfit(potential[lowRang], lowJk, 1)
    lowFit = poly1d(lowfit)
    highfit = polyfit(potential[highRang], highJk, 1)
    highFit = poly1d(highfit)
    conv = WE.area.big()*1e3/WE.mCatCen
    #get acts
    
    acts = {key: {mode: {potential: factor*10**fit(potential)
                for potential in [0.9,0.85,0.8]}
                for mode, factor in [("area", 1), ("mass", conv)]}
                for key, fit in [("low", lowFit), ("high", highFit)]}
    #TODO: report slopes
    print lowfit
    acts['tafel'] = 1/lowfit[0]
    #copy to excel
    if copy:
        toClipboardForExcel(column_stack((potential, logJk)))
        raw_input("copy ...")
        print '... done'
        toClipboardForExcel(column_stack((potential, lowJk)))
        raw_input("copy ...")
        print '... done'
        toClipboardForExcel(column_stack((potential, logJk)))
        raw_input("copy ...")
        print '... done'
    #plot
    if graph:#graph:
        plt.figure()
        plt.plot(potential, logJk, ":")
        plt.plot(potential[lowRang], lowFit(potential[lowRang]))
        plt.plot(potential[highRang], highFit(potential[highRang]))
        #plt.plot(highJk, potential[highRang])
        plt.xlabel('Potencial (V)')
        plt.ylabel('log Jk (A/cm2 Pt)')
        plt.title("Tafel")
        plt.show()
    return acts

def KL(cycles, WE, graph=True, copy=False):#rpm, cycle, WE, graph=True):
    #TODO: mejor x, y, array
    x, y = [], []
    for rpm, cycle in cycles.iteritems():
        #same as in Tafel
        potential = cycle[:,0]
        current = cycle[:,1]
        rang = (potential>0.2)[1:] & (diff(potential)>=0)
        potential = potential[rang]
        current = current[rang]
        #current density
        current = current/WE.area.geom
        #JL
        JLrang = (potential>0.2) & (potential<0.4)
        JL = average(current[JLrang])
        x.append(float(rpm)**-0.5) 
        y.append(-1.0/JL)
    m, b = polyfit(x, y, 1) #mA/(cm^2*rpm^.5)
    #copy to excel
    if copy:
        toClipboardForExcel(column_stack((x, y)))
        raw_input("copy KL...")
        print m, b, '... done'
    if graph:
        plt.figure()
        plt.plot(x, [m*i+b for i in x])
        plt.scatter(x, y)
        plt.xlabel('RPM^-0.5 (s^-0.5)')
        plt.ylabel('JL (cm2/A)')
        plt.title("KL")
        plt.show()
    return 1/m