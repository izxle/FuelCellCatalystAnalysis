import re
from configparser import ConfigParser
from os import path


class Params(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        name = str(key)
        setattr(self, name, value)
        super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, "
                                f"got {len(args)}")
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]


def parse_config_values(config):
    params = Params()
    for sec in config.sections():
        params[sec] = Params()
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
            elif value.lower() in {'false', 'true', 'on', 'off', 'yes', 'no'}:
                value = value.lower() in {'true', 'on', 'yes'}
            params[sec][name] = value
    return params


def read_config(fname):
    config = ConfigParser(allow_no_value=True)
    assert path.isfile(fname), f'{fname} does not exist, must be an existing file'

    config.read(fname)

    # read directory path from GENERAL section
    directory = config['GENERAL']['path']
    # extract path to directory
    assert path.isdir(directory), f'{directory} must be an existing directory'

    params = parse_config_values(config)

    return params
