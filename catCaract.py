from getdata2 import *
from electrode import *
from re import search
from arraytoexcel import toClipboardForExcel
import CV, CO, ORR
import matplotlib.pyplot as plt
import sys
#init
def runAll(fpath=None, ext = ".txt", COnam=None, CVnam=None, bCV=True, bCO=True,
            mCat=5., vSolv=2., pCatCen=30., area=0.196, vInk=10., addH=True,
            CVsr=50., CVrangLow=0.4, CVrangHigh=0.6, COrangCOHigh=1.,
            COsr=20., COrangCLow=0.4, COrangCHigh=0.6, COrangCOLow=0.6,
            ORRrangLow=0.2, ORRrangHigh=0.4, ORRshift=1.0, ORRsr=20., bORR=True,
            verb=False, graph=[0,0,0,0], copy=False, MEA=False, retFold=False,
            CVfirst=False):
    #graph = [CV, CO, Tafel, KL]
    #init
    #electrode and ink data
    ink = Ink(mCat=mCat, vSolv=vSolv, pCatCen=pCatCen)
    WE = Electrode(area=0.196, ink=ink, vInk=vInk)
    #get filenames cn folder
    folder = Folder(fpath=fpath, ext=ext, verb=verb)
    #TODO: get useful file names
    nams = folder.getNams()
    if verb: print nams
    #TODO: mejorar
    #runs
    if bCV:
        Vars = {'sr': CVsr, 'rCl': CVrangLow, 'rCu': CVrangHigh,
                'copy': copy, 'graph': graph[0]}
        CVpath = '\\' + CVnam + ext
        fCV = folder.getCycles(CVpath)[1] if CVfirst else None
        cCV = folder.getCycles(CVpath, last=True)
        aCV = CV.H(cCV, fCV=fCV, **Vars)
        WE.area.update(CV=aCV)
    if bCO:
        Vars = {'sr': COsr, 'rCl':COrangCLow, 'rCu': COrangCHigh, 'graph': graph[1],  
                'rCOl': COrangCOLow, 'rCOu': COrangCOHigh, 'copy': copy, 'addH': addH}
        COpath = '\\' + COnam + ext
        cCO = folder.getCycles(COpath)
        aCO, aH = CO.run(cCO, **Vars)
        WE.area.update(CO=aCO, H=aH)
    if bCV or bCO: WE.setECSA()
    if bORR:
        Vars = {'sr': ORRsr, 'rL': ORRrangLow, 'rU': ORRrangHigh,
                'par': ORRshift, 'copy': copy, 'graph': graph[2]}
        ORRfiles = {int(search("[0-9]+00", nam).group(0)): nam for nam in nams if "00" in nam}
        cTafel = folder.getCycles(ORRfiles[1600])[1]
        #TODO: get ciclo util
        WE.setActs(ORR.tafel(cTafel, WE, **Vars))
        #KL
        cORR = {val: folder.getCycles(nam)[1] for val, nam in ORRfiles.items()}
        WE.setKL(ORR.KL(cORR, WE, graph=graph[3], copy=copy))
    return (WE, folder) if retFold else WE