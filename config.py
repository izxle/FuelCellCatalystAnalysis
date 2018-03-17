import re
from configparser import ConfigParser
from os import path


class Params(object):
    def set(self, name, value):
        setattr(self, name, value)


def read_config(fname):
    config = ConfigParser(allow_no_value=True)
    assert path.isfile(fname), f'{filename} does not exist, must be an existing file'

    config.read(fname)

    params = Params()

    # read GENERAL section
    general = config['GENERAL']
    # extract path to directory
    params.path = general['path']
    assert path.isdir(params.path), f'{params.path} does not exist, must be an existing directory'

    for sec in config.sections():
        for name, value in config.items(sec):
            if '\n' in value:
                value = list(map(str.strip, value.split('\n')))
            # int values
            elif re.match('-?\d+$', value):
                value = int(value)
            # float values
            elif re.match('-?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$', value):
                value = float(value)
              

    # TODO: config parser
    params = dict()
    return params
