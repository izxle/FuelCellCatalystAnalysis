import matplotlib.pyplot as plt
from numpy import average, diff, log10, column_stack, zeros, empty
from pylab import polyfit, poly1d

from arraytoexcel import toClipboardForExcel


class Activities:
    def __init__(self):
        self.mass = None
        self.area = None

    def set_mass_activity(self, activity):
        self.mass = activity

    def set_area_activity(self, activity):
        self.area = activity


def unzipos(cycle, verb=False):
    # x, y = hsplit(cycle, 2)
    x, y = cycle

    if verb > 2: print('     init unzip', len(x))
    rang = diff(x) > 0
    if verb > 2: print('     positives:', rang.sum())
    x = x[1:][rang]
    y = y[1:][rang]

    if len(x) == 0: raise Exception('Error in splitting. ORR.')
    if verb > 2: print('     diff', len(x))

    rang = zeros(len(x), dtype=bool)
    prev_E = -float('inf')

    for ix, E in enumerate(x):
        if E < prev_E:
            break
        rang[ix] = True
        prev_E = E

    if rang.sum() == 1:
        rang[0] = False
        prev_E = x[ix]

        for ix, E in enumerate(x[ix + 1:], ix + 1):
            if E < prev_E:
                break
            rang[ix] = True
            prev_E = E

    x = x[rang]
    y = y[rang]

    if verb > 2: print('     fin unzip', len(x))

    return x, y


def tafel(cycle, base=None, limit_current_range=(1.5, 20), sweep_rate=20, catalyst_mass=None, area=None,
          shift=1.5, graph=True, copy=False, rpm=1600, verb=False, report='area mass', activity_potential=0.9):
    # unzip data
    iL_lower, iL_upper = limit_current_range
    potential, current = cycle

    verb > 2 and print(f'    cycle <{cycle.shape}>')
    if graph > 1:
        plt.figure(f'ORR - Tafel - {rpm} - positive sweep')
        plt.plot(potential, current, label='Raw data')
    # cut for useful data
    # TODO: add another filter
    rang = iL_lower < potential
    potential = potential[rang]
    current = current[rang]
    verb > 2 and print(f'    cut down to <{len(current)}>')
    # TODO: interpolate base to ignore it's size
    if base is not None:
        xB, yB = base
        # extra_data_before = len(yB) - len(rang)
        # yB = yB[extra_data_before:]
        yB = yB[rang]
        assert len(current) == len(yB), f'cycle<{len(current)}> and base<{len(base)}> have different length.'
    else:
        yB = empty(len(current), dtype=float)
        yB[:] = current[-1]
        # yB = array([current[-1] for i in range(len(current))])
    if graph > 1:
        plt.plot(potential, current, label='Diffusion limited region')
    # remove base
    current -= yB

    if graph > 1:
        plt.plot(potential, current, label='Corrected data')
        plt.legend()
    # current to specific density [A / cm^2 Pt]
    current_density = current / area
    # get diffusion controled current JL
    # TODO: auto cut
    JLrang = (potential > iL_lower) & (potential < iL_upper)
    JL = average(current[JLrang])
    verb > 2 and print(f'      JL <{JLrang.sum()}> = {JL}')
    # correction 2 get Jk, cut @ upper limit for noise
    # TODO: auto cut
    rang = (potential > iL_upper) & (current != JL) & (current != 0)
    potential = potential[rang]
    current = current[rang]
    verb > 2 and print(f'    cut down to <{len(current)} to match>')
    Jk = current * JL / (JL - current)

    # TODO: get Ik @ 0.9V for acts

    # tafel slopes calcs
    # to log scale
    logJk = log10(abs(Jk))
    # TODO: calc tafel rangs
    # get points cn pend neg
    negS = diff(logJk) < 0
    potential = potential[1:][negS]
    current = current[1:][negS]
    logJk = logJk[1:][negS]
    lowCh = logJk[-1] + shift  # arbitrario TODO: calc
    ##
    lowRang = (logJk > lowCh) & (logJk < lowCh + 1)
    highRang = (logJk > lowCh + 1) & (logJk < lowCh + 2)
    # TOpatch: start ~0.92V

    verb > 2 and print(f'    negative slope <{len(current)}>')

    ##
    ##
    # lowRang = (logJk>-4.53) & (logJk<-3.53)
    # highRang = (logJk>-3.53) & (logJk<-2.53)
    lowJk = logJk[lowRang]
    highJk = logJk[highRang]
    lowfit = polyfit(potential[lowRang], lowJk, 1)
    lowFit = poly1d(lowfit)
    highfit = polyfit(potential[highRang], highJk, 1)
    highFit = poly1d(highfit)

    if area is not None:
        factor_area = 1 / area
    if catalyst_mass is not None:
        factor_mass = 1e3 / catalyst_mass
    # get acts
    low_current = 10 ** lowFit(potential)
    high_current = 10 ** highFit(potential)


    acts = {key: {mode: {potential: factor * 10 ** fit(potential)
                         for potential in [0.9, 0.85, 0.8]}
                  for mode, factor in [("area", 1), ("mass", conv)]}
            for key, fit in [("low", lowFit), ("high", highFit)]}
    # TODO: report slopes
    # print lowfit
    acts['tafel'] = {}
    acts['tafel']['low'] = 1 / lowfit[0]
    acts['tafel']['high'] = 1 / highfit[0]
    # copy to excel
    if copy:
        toClipboardForExcel(column_stack((potential, logJk)))
        input("copy logJk...")
        print('... done')
        toClipboardForExcel(column_stack((potential[lowRang], lowJk)))
        input("copy lowJk...")
        print('... done')
        toClipboardForExcel(column_stack((potential[highRang], highJk)))
        input("copy highJk...")
        print('... done')
    # plot
    if graph:  # graph:
        plt.figure('ORR - Tafel')
        plt.plot(potential, logJk, ":")
        plt.plot(potential[lowRang], lowFit(potential[lowRang]))
        plt.plot(potential[highRang], highFit(potential[highRang]))
        # plt.plot(highJk, potential[highRang])
        plt.xlabel('Potencial (V)')
        plt.ylabel('log Jk (A/cm$^2_{Pt}$)')
        plt.title("Tafel")
        # plt.show()
    return acts


def KL(cycles, WE, graph=True, copy=False):  # rpm, cycle, WE, graph=True):
    # TODO: subtract base
    x, y = [], []
    for rpm, cycle in list(cycles.items()):
        # same as in Tafel
        potential = cycle[:, 0]
        current = cycle[:, 1]
        rang = (potential > 0.2)[1:] & (diff(potential) >= 0)
        potential = potential[1:][rang]
        current = current[1:][rang]
        # current density
        current = current / WE.area.geom
        # JL
        JLrang = (potential > 0.2) & (potential < 0.4)
        JL = average(current[JLrang])
        x.append(float(rpm) ** -0.5)
        y.append(-1.0 / JL)
    m, b = polyfit(x, y, 1)  # mA / (cm^2 * rpm^.5)
    # copy to excel
    if copy:
        toClipboardForExcel(column_stack((x, y)))
        input("copy KL...")
        print((m, b, '... done'))
    if graph:
        # TODO: add equation to graph
        plt.figure('ORR - Koutecký-Levich')
        plt.plot(x, [m * i + b for i in x])
        plt.scatter(x, y)
        plt.xlabel('RPM$^{-0.5}$ (s$^{-0.5}$)')
        plt.ylabel('JL (cm$^2$ / A)')
        plt.title("Koutecký-Levich")
        # plt.show()
    return 1 / m


def plot(cycles, graph=True, base=None, copy=False, verb=False):
    if base is not None:
        xB, yB = base
    else:
        xB, yB = None, None

    for rpm, cycle in list(cycles.items()):
        verb and print('    plotting ORR', rpm)
        # x, y = unzipos(cycle, verb)
        x, y = cycle
        # plot
        if graph:
            plt.figure('ORR - Raw data')
            plt.plot(x, y, label=str(rpm))
            if yB is not None:
                y -= yB
                plt.figure('ORR - Corrected data')
                plt.plot(x, y, label=str(rpm))
        # copy to excel
        if copy:
            toClipboardForExcel(column_stack((x, y)))
            input("copy ORR {}...".format(rpm))
            print('  ... done')
    if graph:
        plt.figure('ORR - Raw data')
        plt.title('ORR - Linear Voltammogram - Raw positive sweeps')
        plt.legend(title='RPM', loc=0)
        plt.xlabel('Potential (V)')
        plt.ylabel('Current (A)')

        plt.figure('ORR - Corrected data')
        plt.title('ORR - Voltammogram - Positive sweeps')
        plt.xlabel('Potential (V)')
        plt.ylabel('Current (A)')
        if yB is not None:
            plt.plot(xB, yB, 'g:', label='Baseline')
        plt.legend(title='RPM', loc=0)


def run(orr_data, exe='', graph=False, rpm='1600', verb=False, **params):
    cycles = dict()
    for name, data in orr_data.items():
        linear_sweep = unzipos(data.get_scan(-1))
        if name == 'background':
            baseline = linear_sweep
        else:
            cycles[name] = linear_sweep

    if 'ORR' in exe:
        verb and print('  init plottting')
        plot(cycles, graph=graph, copy=params['copy'], verb=verb, base=baseline)
        verb and print('  fin plottting')
    if 'tafel' in exe:
        cycle = cycles[rpm]
        verb and print('  init tafel')
        acts = tafel(cycle, graph=graph, verb=verb, **params)
        verb and print('  fin tafel')
        WE.setActs(acts)
    if 'KL' in exe:
        verb and print('  init KL')
        # B = KL(data, WE, graph=graph, copy=params['copy'])
        verb and print('  fin KL')
        # WE.setKL(B)
    if graph:
        pass
        # plt.show()
    return True
