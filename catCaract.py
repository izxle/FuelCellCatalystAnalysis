from getdata import *
from electrode import *
from re import search
from arraytoexcel import toClipboardForExcel
import CV, CO, ORR
import matplotlib.pyplot as plt
import sys
#init
def runAll(fpath, ink_params, electrode_params,
           CV_params, CO_params, ORR_params,
           verb):
    #--INIT--
    # ink and electrode data
    if verb: print 'fpath:', fpath
    ink = Ink(**ink_params)
    WE = Electrode(ink=ink, **electrode_params)
    
    # get filenames cn folder
    #TODO: auto get ORR nams
    nams = [obj.get("nam") for obj in [CV_params, CO_params, 
                                        ORR_params] if obj.get("nam")]
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
        # get cycles
        first = data.getCycle(CO_params['nam'], 1)
        second = data.getCycle(CO_params['nam'], 2)
        # get areas from CO and H
        aCO, aH = CO.run(first, second, **params)
        # store areas
        WE.area.update(CO=aCO, H=aH)
        if verb: print ".. CO done."
    # set ECSA if area from CV.H, CO.H or CO.CO
    WE.setECSA()
    
    if ORR_params['run'] and WE.ECSA:
        if verb: print "Running ORR.."
        params = ORR_params
        del params['nams']
        # get RPM values from nams
        nams = {int(search("[0-9]+00", nam).group(0)): nam
                for nam in ORR_params['nams'] if "00" in nam}
        # get last cycle
        #TODO: input cycle
        cycle = data.getCycle(nams[1600], -1)
        # calc and  store activities
        WE.setActs(ORR.tafel(cycle, WE, **params))
        #KL
        cORR = {val: data.getCycle(nam, -1)
                for val, nam in nams.iteritems()}
        WE.setKL(ORR.KL(cORR, WE, graph=graph[3], copy=copy))
        if verb: print ".. ORR done."

    return WE