import re
from configparser import ConfigParser
from os import path, chdir


section_default = {
    'data directory': '.',
    'ext': '',
    'delimiter': ';'
}


class DictWithAttrs(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        name = str(key).lower().replace(' ', '_')
        super().__setattr__(name, value)
        super().__setitem__(key, value)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
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


class Params(DictWithAttrs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.catalyst = dict()
        self.electrode = dict()
        self.ink = dict()
# ..
# TODO: create classes for each section
# TODO: get sweep rate from data

def parse_analysis_sections(cv=None, co=None, orr=None):
    cv_params = DictWithAttrs(exe=cv.run,
                              data=cv.filename,
                              sweep_rate=cv.get('sweep_rate'),
                              c_range=cv.c_range,
                              first=cv.first,
                              graph=cv.graph,
                              copy=cv.copy)

    co_params = DictWithAttrs(exe=co.run,
                              data=co.filename,
                              sweep_rate=co.get('sweep_rate'),
                              c_range=co.c_range,
                              co_range=co.co_range,
                              graph=co.graph,
                              copy=co.copy)

    files_orr = dict()
    for filename in orr.filenames:
        match = re.search('\d?\d00', filename)
        if match:
            rpm = match.group()
            files_orr[rpm] = filename
        else:
            # TODO: log warning
            pass

    if orr.background:
        files_orr['background'] = orr.background

    orr_params = DictWithAttrs(exe=orr.run,
                               data=files_orr,
                               area=orr.area,
                               sweep_rate=orr.get('sweep_rate'),
                               limit_current_range=orr.limit_current_range,
                               rpm=orr.rpm,
                               report=orr.report,
                               shift=orr.shift,
                               graph=orr.graph,
                               copy=orr.copy)

    analysis_params = DictWithAttrs(cv=cv_params,
                                    co=co_params,
                                    orr=orr_params)
    return analysis_params


def parse_config_values(config: ConfigParser) -> Params:
    params = Params()
    filenames = list()
    # iterate through the name of the sections
    for sec in config.sections():
        params[sec] = DictWithAttrs()
        for name, value in config.items(sec):
            if name == 'delimiter' and value == 'tab':
                value = '\t'
            elif name == 'run':
                value = re.split('\s*[, ]\s*', value)
            elif 'range' in name:
                value = re.split('\s*[, ]\s*', value)
                assert len(value) == 2, f'{name} must have 2 values, found {len(value)}'
            elif name in {'filename', 'background'}:
                value = value.replace('\\', '/')
                filenames.append(value)
            elif name == 'filenames':
                value = list(map(str.strip, value.strip().split('\n')))
                filenames.extend(value)
            elif '\n' in value:
                value = list(map(str.strip, value.strip().split('\n')))
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

            if value == ['']:
                value = list()
            elif 'range' in name:
                value = list(map(float, value))
            params[sec][name] = value
    params['GENERAL']['filenames'] = filenames

    return params


def read_config(fname: str) -> Params:

    config = ConfigParser(allow_no_value=True)
    fname = fname.replace('\\' ,'/')
    assert path.isfile(fname), f'{fname} does not exist, must be an existing file'

    config['DEFAULT'] = section_default
    config.read(fname)

    cwd = path.dirname(fname)
    if cwd:
        chdir(cwd)

    # read directory path from GENERAL section
    directory = config['GENERAL'].get('data directory')
    # extract path to directory
    assert path.isdir(directory), f'{directory} must be an existing directory'

    params = parse_config_values(config)

    params['ANALYSIS'] = parse_analysis_sections(cv=params.cv,
                                                 co=params.co,
                                                 orr=params.orr)

    return params

