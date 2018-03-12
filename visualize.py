import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

labels = dict(potential='Potential / V',
              current='Current / A',
              time='Time / s')


def view(data, x_name='', y_name='', cycle=0, title='', fig_num='', smooth='', log_level=0):
    if cycle == -1:
        cycle = data.scan.max()
    # mask = data[:, 2] == cycle if cycle else Ellipsis
    mask = data.scan == cycle if cycle else Ellipsis

    x = data.get_property(x_name)[mask]
    y = data.get_property(y_name)[mask]

    # x = data[:, 0][mask]
    # y = data[:, 1][mask]

    f = plt.figure(fig_num)
    ax = f.add_subplot(111)
    ax.plot(x, y)
    if smooth:
        y_smooth = savgol_filter(y, 5, 3)
        ax.plot(x, y_smooth)

    if not title:
        title = data.name
    ax.set_title(title)
    ax.set_xlabel(labels[x_name])
    ax.set_ylabel(labels[y_name])
    ax.set_xlim(-10, 300)
