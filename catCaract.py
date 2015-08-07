from getdata import *
from electrode import *
from re import search
from arraytoexcel import toClipboardForExcel
import CV, CO, ORR
import matplotlib.pyplot as plt
import sys

#TODO: add verbosity to CV, CO, electrode, getdata

#init
def runAll(fpath, ink_params, electrode_params,
           CV_params, CO_params, ORR_params, ECSA='CO',
           verb=False):
    #--INIT--
    # ink and electrode data
    if verb: print 'fpath:', fpath
    ink = Ink(**ink_params)
    WE = Electrode(ink=ink, **electrode_params)
    
    # get filenames cn folder
    #TODO: auto get ORR nams
    nams = [obj['nam'] for obj in [CV_params, CO_params] if obj["run"]]
    if ORR_params['run']:
        nams += ORR_params['nams']
    
    if verb: print 'nams:', nams
    data = Folder(path=fpath, nams=nams, verb=verb)
    if verb: print 'data.nams:', data.nams
    
    #--RUNS--
    if CV_params['run']:
        if verb: print "Running CV.."
        params = dict(CV_params)
        params["exe"] = params["run"]
        del params["run"]
        del params["nam"]
        if params['first']:
            params['first'] = data.getCycle(CV_params['nam'], 1)
        # get last cycle
        #TODO: detect when -1 not complete cycle and use -2
        params["cycle"] = data.getCycle(CV_params['nam'], -1)
        # get area from CV
        aCV = CV.run(**params)
        # store area
        WE.area.update(CV=aCV)
        if verb: print ".. CV done."
       
    if CO_params['run']:
        if verb: print "Running CO.."
        params = dict(CO_params)
        params["exe"] = params["run"]
        del params["run"]
        del params["nam"]
        if params.get('substract', None): del params['substract']
        # get cycles
        first = data.getCycle(CO_params['nam'], 1)
        
        substract = CO_params.get('substract', 2)
        
        second = data.getCycle(CO_params['nam'], substract)
        # get areas from CO and H
        aCO, aH = CO.run(first, second, **params)
        # store areas
        WE.area.update(CO=aCO, H=aH)
        if verb: print ".. CO done."
    # set ECSA if area from CV.H, CO.H or CO.CO
    WE.setECSA(area=ECSA)
    
    if ORR_params['run']:
        if verb: print "Running ORR.."
        params = dict(ORR_params)
        del params['nams']
        #del params['run']
        # get RPM values from nams
        nams = {int(search("[0-9]+00", nam).group(0)): nam
                for nam in ORR_params['nams'] if "00" in nam}
        # graph
        #TODO: choose rpms
        params['cycles'] = {val: data.getCycle(nam, -1)
                            for val, nam in nams.iteritems()}
        params['WE'] = WE
        params['verb'] = verb
        WE = ORR.run(**params)
        # get last cycle
        ##TODO: input cycle
        #cycle = data.getCycle(nams[1600], -1)
        ## calc and  store activities
        #WE.setActs(ORR.tafel(cycle, WE, **params))
        ##KL
        #cORR = {val: data.getCycle(nam, -1)
        #        for val, nam in nams.iteritems()}
        #WE.setKL(ORR.KL(cORR, WE, graph=graph[3], copy=copy))
        if verb: print ".. ORR done."

    return WE