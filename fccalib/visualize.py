import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from fccalib.reader import Data

labels = dict(potential=('Potential', 'V'),
              current=('Current', 'A'),
              time=('Time', 's'),
              fc_potential=('Potential', 'V'),
              fc_current=('Current', 'A'),
              fc_current_density=('Current density', 'mA/cm²'),
              power=('Power', 'Watts'),
              power_density=('Power density', 'mW/cm²'))

suffix_table = {
    3: 'G',
    2: 'M',
    1: 'k',
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
    if name not in labels:
        return name
    text, units = labels[name]
    label = f'{text} / {suffix}{units}'
    return label


def view(data: Data, x_name: str='', y_name: str='', y2_name: str='',
         cycle=0, title='', fig_num='', smooth='', y_color='b', y2_color='r',
         xlim=None, ylim=None, color_axis=True, direction: str='both', log_level=0):
    """

    :param data:
    :param x_name:
    :param y_name:
    :param y2_name:
    :param cycle:
    :param title:
    :param fig_num:
    :param smooth:
    :param y_color:
    :param y2_color:
    :param xlim: <List[int, int]> default: None
    :param ylim: <List[int, int]> default: None
    :param color_axis: <bool> color the `y` axis with the color of the data set. default: True
    :param direction: <str> [both|fwd|bwrd] default: both
    :param log_level: not implemented
    :return:
    """

    properties = [x_name, y_name]
    if y2_name:
        properties.append(y2_name)

    if direction == 'both':
        cycle = data.get_scan(cycle, properties)

        # if cycle == -1:
        #     cycle = data.scan.max()
        #
        # mask = data[:, 2] == cycle if cycle else Ellipsis
        # mask = data.scan == cycle if isinstance(cycle, int) else Ellipsis
        # x = data.get_property(x_name)[mask]
        # y = data.get_property(y_name)[mask]

    else:
        if direction == 'fwd':
            d = 1
        elif direction == 'bwrd':
            d = -1
        else:
            raise ValueError(f'direction must be [both,fwd,bwd], not {direction}')
        cycle = data.get_linear_sweep(cycle, direction=d, properties=properties)

    x = cycle[0]
    y = cycle[1]

    assert len(x) and len(y), 'No data found'

    order = int(f'{max(abs(y)):.0e}'[-3:])
    power, suffix = get_suffix(order)
    y *= pow(10, -power)

    f = plt.figure(fig_num)
    ax = f.add_subplot(111)

    if smooth:
        y_smooth = savgol_filter(y, 5, 3)
        ax.plot(x, y_smooth, label=data.name, color=y_color)
    else:
        ax.plot(x, y, label=data.name, color=y_color)

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

    if y2_name:
        y2_label = get_label(y2_name)
        y2 = cycle[2]
        # y2 = data.get_property(y2_name)[mask]
        ax2 = ax.twinx()
        ax2.plot(x, y2, color=y2_color)
        if color_axis:
            # change color of ax
            ax.tick_params(axis='y', labelcolor=y_color)
            ax.set_ylabel(y_label, color=y_color)
            ax2.set_ylabel(y2_label, color=y2_color)
            ax2.tick_params(axis='y', labelcolor=y2_color)

        f.tight_layout()
