from glob import glob
from os import path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
from pandas import read_excel


def extract_data(raw_data, headers=None):
    # raw_data = np.copy(res_data)
    if headers is None:
        # default headers
        headers = ['potential', 'current', 'time']
        potential_index = 0
        current_index = 1
        time_index = 2
    else:
        # get index of first potential/current in headers
        try:
            potential_index = next(i for i, h in enumerate(headers)
                                   if 'potential' in h and 'applied' not in h)
        except StopIteration:
            potential_index = next(i for i, h in enumerate(headers)
                                   if 'potential' in h)

        current_index = next(i for i, h in enumerate(headers)
                             if 'current' in h)
        time_index = next(i for i, h in enumerate(headers)
                          if 'time' in h)

    # get data
    res_data = dict()
    res_data['potential'] = np.array(raw_data[:, potential_index], dtype=float)
    res_data['current'] = np.array(raw_data[:, current_index], dtype=float)
    res_data['time'] = np.array(raw_data[:, time_index], dtype=float)

    # check if scan info in headers
    if any('scan' in h for h in headers):
        scan_index = headers.index('scan')
        res_data['scan'] = np.array(raw_data[:, scan_index], dtype=float)
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

    def get_potential(self, scan=None):
        if scan:
            res = self.get_scan(scan)[0]
        else:
            res = np.copy(self.potential)
        return res

    def set_current(self, array):
        self.current = array

    def get_current(self):
        return np.copy(self.current)

    def set_scan(self, array):
        self.scan = array

    def get_scan(self, i: int):
        if i == -1:
            i = max(self.scan)
        elif i == 0:
            i = 1
        mask = self.scan == i
        potential = self.potential[mask]
        current = self.current[mask]
        cycle = np.vstack((potential, current))
        return cycle

    def get_linear_sweep(self, i: int, direction:int = 1):
        cycle = self.get_scan(i)
        x, y = cycle

        if direction == 1:
            diff = np.diff(x) > 0
        elif direction == -1:
            diff = np.diff(x) < 0
        else:
            raise ValueError('argument `direction` must be 1 or -1')

        first_value = diff[0]
        mask_diff = [first_value] + list(diff)
        x = x[mask_diff]
        y = y[mask_diff]

        if len(x) == 0: raise ValueError('Error in splitting cycle.')

        sorted_indices = x.argsort()
        x = x[sorted_indices]
        y = y[sorted_indices]

        return x, y

    def set_time(self, array):
        self.time = array

    def get_time(self):
        return np.copy(self.time)

    def set_property(self, name, value):
        setattr(self, name, value)

    def get_property(self, name):
        return getattr(self, name)

    def __iter__(self):
        for E, i in zip(self.potential, self.current):
            yield (E, i)

    def __getitem__(self, item):
        return self.current[item]


def read_file(filename: str, delimiter: str = ';', log_level: int = 0, name=None, **kwargs):
    # set log level
    # if log_level:
    #     log.setLevel(log_level)

    # read file to get headers
    with open(filename, 'r') as f:
        first_line = f.readline().lower()

    assert delimiter in first_line, f'Delimiter "{delimiter}" not found in headers.'

    headers = list(map(str.strip, first_line.split(delimiter)))

    if name is None:
        name = path.basename(filename)

    raw_data = np.genfromtxt(filename, skip_header=1, delimiter=delimiter)
    data = Data(name=name, raw_data=raw_data, headers=headers)

    return data


def read_xls(filename):
    name = path.basename(filename)
    df = read_excel(filename)
    headers = list(map(str.lower, df.columns))
    raw_data = df.values
    data = Data(name=name, raw_data=raw_data, headers=headers)
    return data


def read_directory(directory: str = '.', filenames: Iterable[str] = None, extension: str = '.txt',
                   delimiter: str = ';'):
    directory = path.abspath(path.expanduser(directory))
    if filenames is None:
        filenames = glob(path.join(directory, '*' + extension))

    data = dict()
    for filename in filenames:
        filepath = path.join(directory, filename)
        if path.isfile(filepath):
            name, ext = path.splitext(filename)
            if ext == '.xlsx':
                data[filename] = read_xls(filepath)
            else:
                data[filename] = read_file(filepath, delimiter)

    return data


if __name__ == '__main__':
    from fccalib.visualize import view

    data = read_file(r"C:\Users\PARSTAT 2273\Dropbox\Nuwb\Echem\PtBi\180215\4ta-PtBi-H\CO_7.txt", delimiter='\t')
    view(data, 'time', 'current')
    view(data, 'potential', 'current')
    plt.show()
