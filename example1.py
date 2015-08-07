# -*- coding: utf-8 -*-
from catCaract import runAll
path=r"C:\Users\user\Documents\GitHub\FuelCellCatalystAnalysis\examples\data1"
path = path.replace("\\", "/")

kwargs = {'fpath': path, #path to directory with data
    'ink_params': {
            'mCat': 2.5075, #mg
            'vSolv': 1.920, #mL
            'pCatCen': 30.
           },
    'electrode_params':{
                 'area': 0.196, 
                 'vInk': 10.
                },
    'CV_params': {
           'run': '',
           'nam': 'GO30%Pt311014jCV2_3.txt', 
           'sr': 50.,
           # cutoff limits
           #TODO: automize
           'C_lower': 0.49, 'C_upper': 0.6,
           # plotting opts
           'first': False,
           'graph': True,
           'copy': False
          },
    'CO_params': {
           'run': 'H CO', 
           'nam': 'GO30%Pt311014jCO1_2.txt', 
           'sr': 20.,
           # cutoff limits
           'C_lower': 0.4, 'C_upper': 0.6, 
           'CO_lower': 0.6, 'CO_upper':.9,
           # plotting opts
           'graph': 3,
           'copy': False
          },
    'ORR_params': {
            'run': False, 
            'nam': [ #TODO: auto get nams
                     'GO30%Pt311014jORR400-1_5.txt',
                     'GO30%Pt311014jORR900-1_6.txt',
                     'GO30%Pt311014jORR1600-1_7.txt'
                    ],
            # cutoff limits
            'iL_lower': 0.4, 'iL_upper': 0.5, 
            #TODO: automize shift
            'shift': .1, #arbitrary parameter
            # plotting opts
            'graph': True,
            'copy': False
           },
    'verb': True #verbosity
    }
comp = runAll(**kwargs)
print comp