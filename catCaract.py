from re import search

import CO
import CV
import ORR
from electrode import *
from getdata import *


# TODO: add verbosity to CV, CO, electrode, getdata

# init
def runAll(fpath, ink_params, electrode_params,
           CV_params, CO_params, ORR_params, ECSA='CO',
           delimiter=' ', autolab=False, ext='.txt', verb=False):
    # --INIT--
    # ink and electrode data
    verb and print('fpath:', fpath)
    ink = Ink(**ink_params)
    WE = Electrode(ink=ink, **electrode_params)

    # get filenames with folder
    # TODO: auto get ORR filenames
    filenames = [obj['nam'] for obj in [CV_params, CO_params] if obj["run"]]
    if ORR_params['run']:
        filenames += ORR_params['filenames']
        if ORR_params.get('background'):
            filenames.append(ORR_params['background'])

    verb and print('filenames:\n', '\n'.join(f'  {fn}' for fn in filenames))
    data = Folder(fpath=fpath, filenames=filenames, delimiter=delimiter, autolab=autolab, verb=verb, ext=ext)
    verb and print('data.filenames:', '\n'.join(f'  {fn}' for fn in data.files))

    # --RUNS--
    if CV_params['run']:
        verb and print("Running CV..")
        params = dict(CV_params)
        params["exe"] = params["run"]
        del params["run"]
        del params["nam"]
        if params['first']:
            params['first'] = data.getCycle(CV_params['nam'], 1)
        # get last cycle
        last_cycle = data.getCycle(CV_params['nam'], -2)
        # TODO: fix arbitrary number 10
        if last_cycle.size < 10:
            last_cycle = data.getCycle(CV_params['nam'], -2)
        params['cycle'] = last_cycle
        # get area from CV
        aCV = CV.run(**params)
        # store area
        WE.area.update(CV=aCV)
        verb and print(".. CV done.")

    if CO_params['run']:
        verb and print("Running CO..")
        params = dict(CO_params)
        params["exe"] = params["run"]
        del params["run"]
        del params["nam"]
        if params.get('substract', None):
            del params['substract']
        # get cycles
        first = data.getCycle(CO_params['nam'], 1)

        substract = CO_params.get('substract', 2)

        second = data.getCycle(CO_params['nam'], substract)
        # get areas from CO and H
        aCO, aH = CO.run(first, second, **params)
        # store areas
        WE.area.update(CO=aCO, H=aH)
        verb and print(".. CO done.")
    # set ECSA if area from CV.H, CO.H or CO.CO
    WE.setECSA(area=ECSA)

    if ORR_params['run']:
        verb and print("Running ORR..")
        params = dict(ORR_params)
        del params['filenames']
        if params.get('background'):
            del params['background']
        # del params['run']
        # get RPM values from filenames
        filenames = {int(search("[0-9]+00", nam).group(0)): nam
                     for nam in ORR_params['filenames'] if "00" in nam}
        # graph
        # TODO: choose rpms
        params['cycles'] = {val: data.getCycle(nam, -1)
                            for val, nam in filenames.items()}
        if ORR_params.get('background'):
            params['base'] = data.getCycle(ORR_params['background'], -1)
        params['WE'] = WE
        params['verb'] = verb
        WE = ORR.run(**params)
        # get last cycle
        # TODO: input cycle
        # cycle = data.getCycle(filenames[1600], -1)
        # calc and  store activities
        # WE.setActs(ORR.tafel(cycle, WE, **params))
        # KL
        # cORR = {val: data.getCycle(nam, -1)
        #        for val, nam in filenames.iteritems()}
        # WE.setKL(ORR.KL(cORR, WE, graph=graph[3], copy=copy))
        verb and print(".. ORR done.")
    # plt.show()
    return WE
