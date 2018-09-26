from numbers import Real

from numpy import pi


class Area(object):
    # TODO: maybe inherit d dict
    _format = '6.3f'
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

    def __str__(self):
        txt_CO = f'{self.CO:{self._format}} cm^2' if self.CO is not None else '  None'
        txt_H = f'{self.H:{self._format}} cm^2' if self.H is not None else '  None'
        txt_CV = f'{self.CV:{self._format}} cm^2' if self.CV is not None else '  None'
        text = f'''
Area:
    geom: {self.geom:{self._format}} cm^2
    CO:   {txt_CO}
    CO-H: {txt_H}
    CV-H: {txt_CV}
'''
        return text

    def __format__(self, format_spec):
        return f'{str(self):{format_spec}}'
# ..


class Catalyst(object):
    def __init__(self, name: str, mass: Real,
                 active_center_name: str, active_center_percentage: Real,
                 support_name: str = '', support_mass: Real = None):
        self.ecsa = None
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

    def set_ecsa(self, area_real):
        # m^2 / g
        self.ecsa = area_real * 1e2 / self.active_center.mass

    @property
    def ecsa_str(self):
        if self.ecsa is not None:
            txt = f'{self.ecsa:7.3f} m^2 / g_{self.active_center.name}'
        else:
            txt = 'None'
        return txt

    def __str__(self):
        text = (f'{self.name:14} {self.mass:5.1f} ug\n'
                f'{self.active_center}\n'
                f'ECSA = {self.ecsa_str}')
        return text

    def __format__(self, format_spec):
        return f'{str(self):{format_spec}}'
# ..


class ActiveCenter(object):
    def __init__(self, mass: Real, name: str = '', percentage: Real = 100):
        self.name = name
        self.mass = mass
        if percentage == 100:
            # TODO: implement log
            print('Warning: using an active center percentage of 100%')
        self.percentage = percentage

    def __str__(self):
        name = self.name if self.name else 'Active center'
        return f'{name:13}  {self.mass:5.1f} ug'

    def __format__(self, format_spec):
        return f'{str(self):{format_spec}}'
# ..


class Support(object):
    def __init__(self, name: str = 'Support', mass: Real = 0, percentage: Real = None):
        self.name = name
        self.mass = mass
        self.percentage = percentage

    def __format__(self, format_spec):
        return f'{str(self):{format_spec}}'
# ..


class Solvent(object):
    def __init__(self, volume: Real, name: str = 'Support'):
        self.name = name
        if not isinstance(volume, Real):
            raise ValueError(f'volume: got {type(volume)} expected <Real>')
        self.volume = volume

    def __format__(self, format_spec):
        return f'{str(self):{format_spec}}'
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

    def __str__(self):
        text = (f'{self.area}\n'
                f'{self.catalyst}')
        return text
