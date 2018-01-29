# -*- coding: utf-8 -*-
from catCaract import runAll
#TODO: better args
kwargs = {
    'fpath': "<YOUR PATH>/examples/data/", #path to directory with data
    #ink
        'mCat': 2.5075, #mg
        'vSolv': 1.920, #mL
        'pCatCen': 30., 
        'area': 0.196, 
        'vInk': 10.,
    'bCV': True, 
        'CVnam': 'GO30%Pt311014jCV1_1', 
        'CVsr': 50.,
        'CVrangLow': 0.49, 'CVrangHigh': 0.6,
    'bCO': True, 
        'COnam': 'GO30%Pt311014jCO1_2', 
        'COsr': 20., 
        'addH': True,
        'COrangCLow': 0.4, 'COrangCHigh': 0.6, 
        'COrangCOLow': 0.6, 'COrangCOHigh':.9,
    'bORR': True, 
        'ORRrangLow': 0.4, 'ORRrangHigh': 0.5, 
        'ORRshift': .1,
    'verb':False, 
    'ext': '.txt', #extención
    'graph': [1, 1, 1, 1], 
    'copy': False}
comp = runAll(**kwargs)
print(comp)
