from argparse import ArgumentParser

from config import read_config
from electrode_new import Electrode, Ink


def get_args(argv=''):
    parser = ArgumentParser()
    # argument definition
    parser.add_argument('configfile', nargs='?', default='config.ini')
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


def run(argv=''):
    args = get_args(argv)

    config = read_config(args.configfile)

    ink = Ink(**config.Ink)
    # read files and parse data
    electrode = Electrode(ink=ink, **config.Electrode)

    # TODO: add analysis
    electrode.analyze(**config.Analysis)

    return res


if __name__ == '__main__':
    res = run()
    print(res)
