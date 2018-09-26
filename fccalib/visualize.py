import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from fccalib.reader import Data

labels = dict(potential='Potential / V',
              current='Current / A',
              time='Time / s')


def view(data: Data, x_name: str='', y_name: str='', cycle=0, title='', fig_num='', smooth='',
         xlim=None, ylim=None, log_level=0):
    if cycle == -1:
        cycle = data.scan.max()
    # mask = data[:, 2] == cycle if cycle else Ellipsis
    mask = data.scan == cycle if isinstance(cycle, int) else Ellipsis

    x = data.get_property(x_name)[mask]
    y = data.get_property(y_name)[mask]

    # x = data[:, 0][mask]
    # y = data[:, 1][mask]

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
    ax.set_xlabel(labels[x_name])
    ax.set_ylabel(labels[y_name])
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
