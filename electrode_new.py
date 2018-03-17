from numpy import pi

from analysis import Analysis


class Electrode(object):
    def __init__(self, area=None, ink=None, vInk=None, diam=None, MEA=False):
        """
        area: [cm2]
        diam: diametre [cm]
        ink: Ink obj
        vInk: ink volume [uL]
        """
        if MEA:
            self.area = Area(float(area))
            # TODO: side
        else:
            if area:
                self.area = Area(float(area))
                self.diam = (area * 4. / pi) ** 0.5
            elif diam:
                self.diam = float(diam)
                self.area = Area((pi * diam ** 2.) / 4.)
            else:
                raise Exception("Missing area data.")
        self.ink = ink
        self.vInk = float(vInk) if vInk else None
        self.catCen = ink.catCen
        self.mCat = vInk * ink.mCat / ink.vSolv  # ug
        self.mCatCen = self.mCat * ink.pCatCen / 100.  # ug
        self.catLoad = self.mCatCen / self.area.geom  # ug/cm2
        # default None
        self.ECSA = None
        self.acts = {key: {mode: {potential: None
                                  for potential in [0.9, 0.85, 0.8]}
                           for mode in ["area", "mass"]}
                     for key in ["low", "high"]}
        self.acts['tafel'] = {'low': None, 'high': None}
        self.B = None
        # TODO: calc o ask dens
        self.dens = 21.45 if self.catCen == "Pt" else None  # Pt [g/cm3]

    def _calcParticleSize(self):
        self.partSize = 6 * self.mCatCen / (self.dens * self.area.big()) if self.dens else None

    def setKL(self, B):
        self.B = B

    def setECSA(self, area='CO'):
        # chkUnits
        if area == 'CO' and self.area.CO:
            area = self.area.CO
        else:  # elif 'max':
            area = self.area.big()
        self.ECSA = 100. * area / self.catLoad / self.area.geom

    def setActs(self, acts):
        self.acts = acts

    def getRug(self, key=None):
        if key:
            return self.area[key] / self.area.geom
        for key in self.area:
            print((key, "/ geom =", self.area[key] / self.area.geom))

    def analyze(self):
        Analysis()
        return

    def __str__(self):
        blah = (
            """
            Area:
                geom: {0} cm^2
                CO:   {1} cm^2
                CO-H: {2} cm^2
                CV-H: {3} cm^2    
            Deposited ink:
                Volume:        {4} uL
                Catalyst mass: {5} ug
                {6} mass:        {7} ug
                {6} loading: {8} ug/cm^2
            acts@0.9V:
                {9} A/mgPt
                {10} A/cm^2
                {11} V/dec[i]    {14} V/dec[i]
            KL: B = {12}
            Electrochemical Active Area: {13} cm^2/ug{6}
            """)
        try:
            return blah.format(self.area.geom, self.area.CO, self.area.H,
                               self.area.CV, self.vInk, self.mCat, self.catCen, self.mCatCen,
                               self.catLoad, self.acts['low']['mass'][0.9],
                               self.acts['low']['area'][0.9], self.acts['tafel']['low'],
                               self.B, self.ECSA, self.acts['tafel']['high'])
        except TypeError as e:
            print('Electrode print error.')
            return str(e)
        except ValueError as e:
            print([self.area.geom, self.area.CO, self.area.CV, self.area.H,
                   self.vInk, self.mCat, self.catCen, self.mCatCen, self.catLoad,
                   self.acts['low']['mass'][0.9], self.acts['low']['area'][0.9],
                   self.acts['tafel'], self.B, self.ECSA])
            return str(e)


# ..

class Ink(object):
    def __init__(self, catalyst_name=None, catalyst_mass=None, nafion_mass=None,
                 solvent_name=None, solvent_volume=None,
                 support_name=None, support_mass=None,
                 active_center_name="Pt", active_center_mass=None, active_center_percentage=None):
        self.solvent = Solvent(name=solvent_name,
                               volume=solvent_volume)

        self.catalyst = Catalyst(name=catalyst_name,
                                 catalyst_mass=catalyst_mass,
                                 active_center_name=active_center_name,
                                 active_center_percentage=active_center_percentage,
                                 support_name=support_name,
                                 support_mass=support_mass)

        self.catalyst_mass = float(catalyst_mass) if catalyst_mass else None
        self.active_center_name = active_center_name
        self.active_center_mass = float(active_center_mass) if active_center_mass else None
        self.active_center_percentage = float(active_center_percentage) if active_center_percentage else None
        self.nafion_mass = nafion_mass
        self.support_name = support_name
        self.support_mass = float(support_mass) if support_mass else None

    def sample(self, volume=0):
        """

        :param volume: in uL
        :return:
        """
        return


# ..


class Area(object):
    # TODO: maybe inherit d dict
    def __init__(self, geom=None, CO=None, H=None, CV=None):
        self.geom = geom
        self.CO = CO
        self.H = H
        self.CV = CV

    def big(self):
        # TODO: mejorar
        stuff = self.vars()
        stuff['default'] = 1
        del stuff['geom']
        for k, v in self.vars().items():
            if not v:
                del stuff[k]
        maxV = max(stuff.values())
        return maxV  # if maxV else self.geom

    def update(self, **stuff):
        vars(self).update(**stuff)

    def get(self, key):
        return vars(self).get(key)

    def values(self):
        for v in list(vars(self).values()): yield v

    def keys(self):
        for k in list(vars(self).values()): yield k

    def __iter__(self):
        for k in list(vars(self).keys()): yield k

    def __getitem__(self, key):
        return vars(self)[key]

    def vars(self):
        return dict(vars(self))
    # TODO: call


# ..


class Catalyst(object):
    def __init__(self, name, mass, active_center_name, active_center_percentage, support_name=None, support_mass=None):
        self.name = name
        self.mass = mass

        active_center_mass = mass * active_center_percentage
        self.active_center = ActiveCenter(active_center_name, active_center_mass, active_center_percentage)

        self.support = Support(support_name, support_mass)


# ..


class ActiveCenter(object):
    def __init__(self, name, mass, percentage=None):
        self.name = name
        self.mass = mass
        self.percentage = percentage


# ..


class Support(object):
    def __init__(self, name, mass, percentage=None):
        self.name = name
        self.mass = mass
        self.percentage = percentage


# ..


class Solvent(object):
    def __init__(self, name, volume=None):
        self.name = name
        self.volume = volume
# ..
