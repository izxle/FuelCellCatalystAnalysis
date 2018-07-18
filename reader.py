from glob import glob
from os import path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np


def extract_data(res_data, headers=None):
    raw_data = np.copy(res_data)
    if headers is None:
        # default headers
        headers = ['potential', 'current', 'time']
        potential_index = 0
        current_index = 1
        time_index = 2
    else:
        # get index of first potential/current in headers
        potential_index = next(i for i, h in enumerate(headers)
                               if 'potential' in h)
        current_index = next(i for i, h in enumerate(headers)
                             if 'current' in h)
        time_index = next(i for i, h in enumerate(headers)
                          if 'time' in h)

    # get data
    res_data = dict()
    res_data['potential'] = raw_data[:, potential_index]
    res_data['current'] = raw_data[:, current_index]
    res_data['time'] = raw_data[:, time_index]

    # check if scan info in headers
    if any('scan' in h for h in headers):
        scan_index = headers.index('scan')
        res_data['scan'] = raw_data[:, scan_index]
    # calculate scan otherwise
    else:
        round_precision = 3
        # create data object
        m = raw_data.shape[0]
        scan = np.zeros(m)

        init_potential = round(res_data['potential'][0], round_precision)
        scan_num = 0.5
        for i, E in enumerate(res_data['potential']):
            if round(E, round_precision) == init_potential:
                scan_num += 0.5
            scan[i] = int(scan_num)
        res_data['scan'] = scan

    return res_data


class Data(object):
    def __init__(self, name: str = None, raw_data=None, headers=None, *args, **kwargs):
        self.name = name
        self.raw_data = np.array([])
        self.potential = np.array([])
        self.current = np.array([])
        self.scan = np.array([])
        self.time = np.array([])

        data_dict = extract_data(raw_data, headers)
        for name, value in data_dict.items():
            self.set_property(name, value)

    def set_potential(self, array):
        self.potential = array

    def get_potential(self):
        return np.copy(self.potential)

    def set_current(self, array):
        self.current = array

    def get_current(self):
        return np.copy(self.current)

    def set_scan(self, array):
        self.scan = array

    def set_time(self, array):
        self.time = array

    def get_time(self):
        return np.copy(self.time)

    def set_property(self, name, value):
        setattr(self, name, value)

    def get_property(self, name):
        return getattr(self, name)


def read_file(filename: str, delimiter: str = ';', log_level: int = 0, **kwargs):
    # set log level
    # if log_level:
    #     log.setLevel(log_level)

    # read file to get headers
    with open(filename, 'r') as f:
        first_line = f.readline().lower()

    assert delimiter in first_line, f'Delimiter "{delimiter}" not found in headers.'

    headers = list(map(str.strip, first_line.split(delimiter)))

    name = path.basename(filename)
    raw_data = np.genfromtxt(filename, skip_header=1, delimiter=delimiter)
    data = Data(name=name, raw_data=raw_data, headers=headers)

    return data


def read_directory(directory: str = '.', filenames: Iterable[str] = None, extension: str = '.txt',
                   delimiter: str = ';'):
    directory = path.abspath(path.expanduser(directory))
    if filenames is None:
        filenames = glob(path.join(directory, '*' + extension))

    data = list()
    for filename in filenames:
        filepath = path.join(directory, filename)
        if path.isfile(filepath):
            data.append(read_file(filepath, delimiter))

    return data


if __name__ == '__main__':
    from visualize import view

    data = read_file(r"C:\Users\PARSTAT 2273\Dropbox\Nuwb\Echem\PtBi\180215\4ta-PtBi-H\CO_7.txt", delimiter='\t')
    view(data, 'time', 'current')
    view(data, 'potential', 'current')
    plt.show()
