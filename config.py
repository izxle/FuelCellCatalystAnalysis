import re
from configparser import ConfigParser
from os import path


class Params(object):
    def set(self, name, value):
        setattr(self, name, value)


def parse_config_values(config):
    params = dict()
    for sec in config.sections():
        params[sec] = dict()
        for name, value in config.items(sec):
            if name == 'run':
                # TODO: make always list
                value = re.split('[\s]*,?[\s*]', value)
            elif '\n' in value:
                value = list(map(str.strip, value.split('\n')))
            # int values
            elif re.match('-?\d+$', value):
                value = int(value)
            # float values
            elif re.match('-?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$', value):
                value = float(value)
            elif value == r'\t':
                value = '\t'
            # TODO: get bool values
            params[sec][name] = value
    return params


def read_config(fname):
    config = ConfigParser(allow_no_value=True)
    assert path.isfile(fname), f'{filename} does not exist, must be an existing file'

    config.read(fname)

    params = Params()

    # read GENERAL section
    general = config['GENERAL']
    # extract path to directory
    params.path = general['path']
    assert path.isdir(params.path), f'{params.path} must be an existing directory'

    config = parse_config_values(config)

    return params
