import numpy as np

from logger import log


def extract_data(data, headers=None):
    raw_data = np.copy(data)
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
    data = dict()
    data['potential'] = raw_data[:, potential_index]
    data['current'] = raw_data[:, current_index]
    data['time'] = raw_data[:, time_index]

    # check if scan info in headers
    if any('scan' in h for h in headers):
        scan_index = headers.index('scan')
        data['scan'] = raw_data[:, scan_index]
    # calculate scan otherwise
    else:
        round_precision = 3
        # create data object
        m = data.shape[0]
        scan = np.zeros(m)

        init_potential = round(data['potential'][0], round_precision)
        scan_num = 0.5
        for i, E in enumerate(data['potential']):
            if round(E, round_precision) == init_potential:
                scan_num += 0.5
            scan[i] = int(scan_num)
        data['scan'] = scan

    return data


class Data(object):
    def __init__(self, data=None, headers=None, *args, **kwargs):
        self.raw_data = np.array([])
        self.potential = np.array([])
        self.current = np.array([])
        self.scan = np.array([])
        self.time = np.array([])

        data_dict = extract_data(data, headers)
        for name, value in data_dict.items():
            self.set_property(name, value)

    def set_potential(self, array):
        self.potential = array

    def set_current(self, array):
        self.current = array

    def set_scan(self, array):
        self.scan = array

    def set_time(self, array):
        self.time = array

    def set_property(self, name, value):
        setattr(self, name, value)

    def get_property(self, name):
        return getattr(self, name)


def read(filename, log_level=0, delimiter=';', **kwargs):
    # set log level
    if log_level:
        log.setLevel(log_level)

    # read file to get headers
    with open(filename, 'r') as f:
        headers = list(map(str.strip,
                           f.readline().lower().split(delimiter)))

    # get index of first potential/current in headers
    potential_index = next(i for i, h in enumerate(headers)
                           if 'potential' in h)
    current_index = next(i for i, h in enumerate(headers)
                         if 'current' in h)
    # read data
    raw_data = np.genfromtxt(filename, skip_header=1, delimiter=delimiter)

    potential = raw_data[:, potential_index]
    current = raw_data[:, current_index]

    # check if scan info in headers
    if any('scan' in h for h in headers):
        scan_index = headers.index('scan')
        data = raw_data[:, (potential_index, current_index, scan_index)]
    # calculate scan otherwise
    else:
        round_precision = 3
        # create data object
        m = len(potential)
        data = np.zeros((m, 3))
        data[:, 0] = potential
        data[:, 1] = current

        init_potential = round(potential[0], round_precision)
        scan = 0.5
        for i, E in enumerate(potential):
            if round(E, round_precision) == init_potential:
                scan += 0.5
            data[i, 2] = int(scan)

    return data


if __name__ == '__main__':
    from visualize import view

    data = read(r"C:\Users\PARSTAT 2273\Dropbox\Nuwb\Echem\PtBi\180215\4ta-PtBi-H\CO_7.txt", delimiter='\t')
    view(data)
