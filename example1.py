# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

from catCaract import runAll

path = r"C:\Users\PARSTAT 2273\Dropbox\Nuwb\180123"
path = path.replace("\\", "/")

kwargs = {'fpath': path,  # path to directory with data
          'ink_params': {
              'mCat': 10.3,  # mg
              'vSolv': 5,  # mL
              'pCatCen': 20.
          },
          'electrode_params': {
              'area': 0.196,  # cm^2
              'vInk': 10.  # uL
          },
          'CV_params': {
              'run': 'H',
              'nam': 'Pt-ETEK-20% 180123 CV.txt',
              'sr': 50.,
              # cutoff limits
              # TODO: automize
              'C_lower': 0.37, 'C_upper': 0.46,
              # plotting opts
              'first': False,
              'graph': 2,
              'copy': False
          },
          'CO_params': {
              'run': 'H CO',
              'nam': 'Pt-ETEK-20% 180123 CO.txt',
              'sr': 50.,
              # cutoff limits
              'C_lower': 0.4, 'C_upper': 0.6,
              'CO_lower': 0.75, 'CO_upper': 1.,
              # plotting opts
              'graph': 2,
              'copy': False
          },
          'ORR_params': {
              'run': 'ORR tafel KL',
              'filenames': [  # TODO: auto get nams
                  'Pt-ETEK-20% 180123 ORR 400.txt',
                  'Pt-ETEK-20% 180123 ORR 900.txt',
                  'Pt-ETEK-20% 180123 ORR 1600.txt'
                  # 'Pt-ETEK-20% 180123 ORR 2500.txt'
              ],
              # cutoff limits
              'iL_lower': 0.4, 'iL_upper': 0.5,
              # TODO: automize shift
              'shift': .1,  # arbitrary parameter
              # plotting opts
              'graph': 3,
              'copy': False
          },
          'ext': '.txt',
          'delimiter': ';',
          'autolab': True,
          'verb': 1  # verbosity
          }
comp = runAll(**kwargs)
print(comp)
plt.show()
