import matplotlib.pyplot as plt


def view(data, scan=0, log_level=0):
    if scan == -1:
        scan = data[:, 2].max()
    mask = data[:, 2] == scan if scan else Ellipsis

    x = data[:, 0][mask]
    y = data[:, 1][mask]

    f = plt.figure()
    ax = f.add_subplot(111)
    ax.plot(x, y)
    ax.set_title('Raw data')
    ax.set_xlabel('Potential / V')
    ax.set_ylabel('Current / A')
    plt.show()
