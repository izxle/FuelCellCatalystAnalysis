import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from fccalib.reader import Data

labels = dict(potential=('Potential', 'V'),
              current=('Current', 'A'),
              time=('Time', 's'))

suffix_table = {
    3: 'G',
    2: 'M',
    1:'k',
    0: '',
    -1: 'm',
    -2: '$\mu$',
    -3: 'n'}


def get_suffix(order: int):
    index = int(order / 3)
    suffix = suffix_table[index]
    power = index * 3
    return power, suffix


def get_label(name: str, suffix: str='') -> str:
    text, units = labels[name]
    label = f'{text} / {suffix}{units}'
    return label


def view(data: Data, x_name: str='', y_name: str='', cycle=0, title='', fig_num='', smooth='',
         xlim=None, ylim=None, log_level=0):
    if cycle == -1:
        cycle = data.scan.max()
    # mask = data[:, 2] == cycle if cycle else Ellipsis
    mask = data.scan == cycle if isinstance(cycle, int) else Ellipsis

    x = data.get_property(x_name)[mask]
    y = data.get_property(y_name)[mask]

    order = int(f'{max(abs(y)):.0e}'[-3:])
    power, suffix = get_suffix(order)
    y *= pow(10, -power)

    f = plt.figure(fig_num)
    ax = f.add_subplot(111)

    if smooth:
        y_smooth = savgol_filter(y, 5, 3)
        ax.plot(x, y_smooth, label=data.name)
    else:
        ax.plot(x, y, label=data.name)

    if not title:
        title = data.name
    ax.set_title(title)

    x_label = get_label(x_name)
    ax.set_xlabel(x_label)
    y_label = get_label(y_name, suffix)
    ax.set_ylabel(y_label)

    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
