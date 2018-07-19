from numbers import Real

from numpy import pi


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
    def __init__(self, name: str, mass: Real,
                 active_center_name: str, active_center_percentage: Real,
                 support_name: str = '', support_mass: Real = None):
        self.name = name
        self.mass = mass

        active_center_mass = mass * active_center_percentage / 100
        self.active_center = ActiveCenter(mass=active_center_mass,
                                          name=active_center_name,
                                          percentage=active_center_percentage)

        self.support = Support(support_name, support_mass)

    def copy(self, scale: Real = 1):
        sample_catalyst_mass = self.mass * scale
        sample_support_mass = self.support.mass * scale if self.support.mass is not None else None
        catalyst = Catalyst(name=self.name, mass=sample_catalyst_mass,
                            active_center_name=self.active_center.name,
                            active_center_percentage=self.active_center.percentage,
                            support_name=self.support.name,
                            support_mass=sample_support_mass)
        return catalyst


# ..


class ActiveCenter(object):
    def __init__(self, mass: Real, name: str = '', percentage: Real = 100):
        self.name = name
        self.mass = mass
        if percentage == 100:
            # TODO: implement log
            print('Warning: using an active center percentage of 100%')
        self.percentage = percentage
# ..


class Support(object):
    def __init__(self, name: str = 'Support', mass: Real = 0, percentage: Real = None):
        self.name = name
        self.mass = mass
        self.percentage = percentage


# ..


class Solvent(object):
    def __init__(self, volume: Real, name: str = 'Support'):
        self.name = name
        if not isinstance(volume, Real):
            raise ValueError(f'volume: got {type(volume)} expected <Real>')
        self.volume = volume


# ..


class Ink(object):
    def __init__(self, catalyst: Catalyst, solvent: Solvent):
        self.solvent = solvent

        self.catalyst = catalyst

        # TODO: check if aliases are useful
        # aliases
        self.catalyst_mass = catalyst.mass
        self.active_center_name = catalyst.active_center.name
        self.active_center_mass = catalyst.active_center.mass
        self.active_center_percentage = catalyst.active_center.percentage
        self.support_name = catalyst.support.name
        self.support_mass = catalyst.support.mass

    def sample(self, volume: Real = 0) -> Catalyst:
        """
        Returns a Catalyst object with mass corresponding to the provided sample volume
        :param volume: in uL
        :return Catalyst: with mass in ug
        """
        scale = volume / self.solvent.volume
        catalyst = self.catalyst.copy(scale=scale)
        return catalyst


# ..


class Electrode(object):
    def __init__(self, catalyst: Catalyst, area: Real = None, diameter: Real = None):
        if area:
            self.area = Area(float(area))
            self.diameter = (area * 4. / pi) ** 0.5
        elif diameter:
            self.diameter = float(diameter)
            self.area = Area((pi * diameter ** 2.) / 4.)
        else:
            raise ValueError("Missing area or diameter of the electrode.")

        # catalyst with mass in ug
        self.catalyst = catalyst

        catalyst_load = catalyst.active_center.mass / self.area.geom  # ug/cm2
        self.catalyst_load = catalyst_load

        # default activities
        # TODO: create class for catalytic activities

        # self.ECSA = None
        # self.acts = {key: {mode: {potential: None
        #                           for potential in [0.9, 0.85, 0.8]}
        #                    for mode in ["area", "mass"]}
        #              for key in ["low", "high"]}
        # self.acts['tafel'] = {'low': None, 'high': None}
        # self.B = None
        # # TODO: calculate or ask density
        # self.dens = 21.45 if self.catCen == "Pt" else None  # Pt [g/cm3]

#     def _calcParticleSize(self):
#         # TODO: add more geometries
#         # for cuboctahedron
#         self.partSize = 6 * self.mCatCen / (self.dens * self.area.big()) if self.dens else None
#
#     def setKL(self, B):
#         self.B = B
#
#     def setECSA(self, area='CO'):
#         # chkUnits
#         if area == 'CO' and self.area.CO:
#             area = self.area.CO
#         else:  # elif 'max':
#             area = self.area.big()
#         self.ECSA = 100. * area / self.catLoad / self.area.geom
#
#     def setActs(self, acts):
#         self.acts = acts
#
#     def getRug(self, key=None):
#         if key:
#             return self.area[key] / self.area.geom
#         for key in self.area:
#             print((key, "/ geom =", self.area[key] / self.area.geom))
#
#     def analyze(self):
#         Analysis()
#         return
#
#     def __str__(self):
#         blah = (
#             """
#             Area:
#                 geom: {0} cm^2
#                 CO:   {1} cm^2
#                 CO-H: {2} cm^2
#                 CV-H: {3} cm^2
#             Deposited ink:
#                 Volume:        {4} uL
#                 Catalyst mass: {5} ug
#                 {6} mass:        {7} ug
#                 {6} loading: {8} ug/cm^2
#             acts@0.9V:
#                 {9} A/mgPt
#                 {10} A/cm^2
#                 {11} V/dec[i]    {14} V/dec[i]
#             KL: B = {12}
#             Electrochemical Active Area: {13} cm^2/ug{6}
#             """)
#         try:
#             return blah.format(self.area.geom, self.area.CO, self.area.H,
#                                self.area.CV, self.vInk, self.mCat, self.catCen, self.mCatCen,
#                                self.catLoad, self.acts['low']['mass'][0.9],
#                                self.acts['low']['area'][0.9], self.acts['tafel']['low'],
#                                self.B, self.ECSA, self.acts['tafel']['high'])
#         except TypeError as e:
#             print('Electrode print error.')
#             return str(e)
#         except ValueError as e:
#             print([self.area.geom, self.area.CO, self.area.CV, self.area.H,
#                    self.vInk, self.mCat, self.catCen, self.mCatCen, self.catLoad,
#                    self.acts['low']['mass'][0.9], self.acts['low']['area'][0.9],
#                    self.acts['tafel'], self.B, self.ECSA])
#             return str(e)
# # ..
