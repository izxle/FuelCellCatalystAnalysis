
from argparse import ArgumentParser

import matplotlib.pyplot as plt
from pynumparser import NumberSequence

from fccalib.reader import read_file
from fccalib.visualize import view


def get_args(argv=''):

    parser = ArgumentParser()

    parser.add_argument('type', choices=['cv'])
    parser.add_argument('filenames', nargs='+')
    parser.add_argument('-c', '--cycles', type=NumberSequence(), nargs='?', default=-1)
    parser.add_argument('--xlim', nargs=2, type=float)
    parser.add_argument('--smooth', action='store_true')

    # read arguments
    if argv:
        if isinstance(argv, str):
            argv = argv.split()
        elif hasattr(argv, '__iter__'):
            if not all(isinstance(e, str) for e in argv):
                raise ValueError(f'all elements of argv must be string.')
        else:
            raise ValueError(f'argv must be iterable.')
        args = parser.parse_args(argv)
    else:
        args = parser.parse_args()

    return args


def preview_CV(filenames, scan: int=None, xlim=None, smooth=False):
    for fname in filenames:
        data = read_file(fname)
        view(data, 'potential', 'current', cycle=scan,
             title='CV',
             xlim=xlim,
             smooth=smooth)

    plt.legend()


def main(argv=None):
    args = get_args(argv)

    if args.type == 'cv':
        preview_CV(filenames=args.filenames, scan=args.cycles, xlim=args.xlim, smooth=args.smooth)

    plt.show()


if __name__ == '__main__':
    main('cv '
         '../examples/Pt/900.xlsx '
         '../examples/Pt/1600.xlsx '
         '../examples/Pt/2500.xlsx '
         '../examples/Pt/400.xlsx '
         '--xlim 0.2 1 '
         '--smooth')