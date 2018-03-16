from argparse import ArgumentParser

from config import read_config
from electrode import Electrode


def get_args(argv=''):
    parser = ArgumentParser()
    # argument definition
    parser.add_argument('configfile')
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

    config = read_config(args.config)
    electrode = Electrode(**config.Electrode)

    # TODO: add analysis
    config.Analysis

    return electrode


if __name__ == '__main__':
    run(argv='')
