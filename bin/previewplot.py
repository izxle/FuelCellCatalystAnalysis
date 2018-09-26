
from argparse import ArgumentParser

import matplotlib.pyplot as plt

from fccalib.reader import read_file
from fccalib.visualize import view


def get_args(argv=''):
    # general parser
    parser = ArgumentParser()
    # arguments
    parser.add_argument('--cv', nargs='+')

    cvparser = ArgumentParser(prefix_chars='+')
    cvparser.add_argument('filename')
    cvparser.add_argument('+t', '++type')

    # read arguments
    if argv:
        if isinstance(argv, str):
            argv = argv.split()
        elif not hasattr(argv, '__iter__'):
            raise ValueError(f'argv must be iterable.')
        args = parser.parse_args(argv)
    else:
        args = parser.parse_args()
    return args



def preview_CV(filename, scan: int=None):
    data = read_file(filename)
    view(data, 'potential', 'current', cycle=scan, title='CV')


def main(argv=None):
    args = get_args(argv)
    if args.cv:
        preview_CV(args.cv)

    plt.show()


if __name__ == '__main__':
    main()