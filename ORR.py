import matplotlib.pyplot as plt
from numpy import average, diff, log10, column_stack, zeros, empty
from pylab import polyfit, poly1d

from arraytoexcel import toClipboardForExcel


def unzipos(cycle, verb=False):
    # x, y = hsplit(cycle, 2)
    x, y = cycle[:, 0], cycle[:, 1]

    if verb > 2: print('     init unzip', len(x))
    rang = diff(x) > 0

    x = x[1:][rang]
    y = y[1:][rang]

    if len(x) == 0: raise Exception('Error in splitting. ORR.')
    if verb > 2: print('     diff', len(x))

    rang = zeros(len(x), dtype=bool)
    prev_E = -float('inf')

    # ix = 0
    # while x[ix] >= prev_E:
    #     rang[ix] = True
    #     prev_E = x[ix]
    #     ix += 1

    for ix, E in enumerate(x):
        if E < prev_E:
            break
        rang[ix] = True
        prev_E = E

    # rang[0] = True
    # temp = x[0]
    # for i, E in enumerate(x[1:], 1):
    #     if E >= temp:
    #         rang = append(rang, True)
    #     else:
    #         break
    #     temp = E

    if rang.sum() == 1:
        rang[0] = False
        prev_E = x[ix]

        # ix += 1
        # while x[ix] >= prev_E:
        #     rang[ix] = True
        #     prev_E = x[ix]
        #     ix += 1

        for ix, E in enumerate(x[ix + 1:], ix + 1):
            if E < prev_E:
                break
            rang[ix] = True
            prev_E = E

        # raise Exception('Sweep in unsupported direction. ORR.')

    x = x[rang]
    y = y[rang]

    if verb > 2: print('     fin unzip', len(x))

    return x, y


def tafel(cycle, WE=None, base=None, iL_lower=.2, iL_upper=.4,
          shift=1.5, sr=20., graph=True, copy=False, rpm=1600, verb=False, report='area mass'):
    # unzip data
    potential, current = unzipos(cycle, verb)

    verb > 2 and print(f'    cycle <{cycle.shape}>')
    if graph > 1:
        plt.figure(f'ORR - Tafel - {rpm} - positive sweep')
        plt.plot(potential, current, label='Raw data')
    # cut for useful data
    # TODO: add onother filter
    rang = iL_lower < potential
    potential = potential[rang]
    current = current[rang]
    verb > 2 and print(f'    cut down to <{len(current)}>')
    if base:
        xB, yB = unzipos(base)
        assert len(current) == len(yB), f'cycle<{len(current)}> and base<{len(base)}> have different length.'
        yB = yB[rang]
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
    # current to specific density [A/cm2 Pt]
    current /= WE.area.big()
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
    conv = WE.area.big() * 1e3 / WE.mCatCen
    # get acts

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
        eval(input("copy logJk..."))
        print('... done')
        toClipboardForExcel(column_stack((potential[lowRang], lowJk)))
        eval(input("copy lowJk..."))
        print('... done')
        toClipboardForExcel(column_stack((potential[highRang], highJk)))
        eval(input("copy highJk..."))
        print('... done')
    # plot
    if graph:  # graph:
        plt.figure('ORR - Tafel')
        plt.plot(potential, logJk, ":")
        plt.plot(potential[lowRang], lowFit(potential[lowRang]))
        plt.plot(potential[highRang], highFit(potential[highRang]))
        # plt.plot(highJk, potential[highRang])
        plt.xlabel('Potencial (V)')
        plt.ylabel('log Jk (A/cm2 Pt)')
        plt.title("Tafel")
        # plt.show()
    return acts


def KL(cycles, WE, graph=True, copy=False):  # rpm, cycle, WE, graph=True):
    # TODO: substract base
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
    m, b = polyfit(x, y, 1)  # mA/(cm^2*rpm^.5)
    # copy to excel
    if copy:
        toClipboardForExcel(column_stack((x, y)))
        eval(input("copy KL..."))
        print((m, b, '... done'))
    if graph:
        # TODO: add equation to graph
        plt.figure('ORR - Koutecký-Levich')
        plt.plot(x, [m * i + b for i in x])
        plt.scatter(x, y)
        plt.xlabel('RPM^-0.5 (s^-0.5)')
        plt.ylabel('JL (cm2/A)')
        plt.title("KL")
        # plt.show()
    return 1 / m


def plot(cycles, graph=True, copy=False, verb=False):
    if graph:
        plt.figure('ORR - Raw data')
    for rpm, cycle in list(cycles.items()):
        if verb: print('    plotting ORR', rpm)
        x, y = unzipos(cycle, verb)
        # copy to excel
        if copy:
            toClipboardForExcel(column_stack((x, y)))
            eval(input("copy ORR {}...".format(rpm)))
            print('  ... done')
        # plot
        if graph:
            plt.plot(x, y, label=str(rpm))
    if graph:
        plt.legend(title='RPM', loc=0)


def run(cycles, WE, run, graph, rpm=1600, verb=False, **params):
    if 'ORR' in run:
        if verb: print('  init plottting')
        plot(cycles, graph=graph, copy=params['copy'], verb=verb)
        if verb: print('  fin plottting')
    if 'tafel' in run and WE.ECSA:
        cycle = cycles[rpm]
        if verb: print('  init tafel')
        acts = tafel(cycle, WE, graph=graph, verb=verb, **params)
        if verb: print('  fin tafel')
        WE.setActs(acts)
    if 'KL' in run:
        if verb: print('  init KL')
        B = KL(cycles, WE, graph=graph, copy=params['copy'])
        if verb: print('  fin KL')
        WE.setKL(B)
    if graph:
        pass
        # plt.show()
    return WE
