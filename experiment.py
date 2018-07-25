import CO
import CV
import ORR
from electrode import Electrode
from reader import Data


class Experiment:
    def __init__(self, data: Data, electrode: Electrode, analysis_params=None):
        self.data = data
        self.electrode = electrode
        self.analysis_params = analysis_params
        if analysis_params is not None:
            self._analyze()

    def set_analysis_params(self, analysis_params):
        self.analysis_params = analysis_params

    def _analyze(self):
        # CV
        cv_params = self.analysis_params.cv
        cv_data = self.data.get(cv_params.data, False)
        if cv_params.exe and cv_data:
            cv_params.data = cv_data
            area_H_CV = CV.run(**cv_params)
            self.electrode.area.CV = area_H_CV
            self.electrode.catalyst.set_ecsa(area_H_CV)

        # CO
        co_params = self.analysis_params.co
        co_data = self.data.get(co_params.data, False)
        if co_params.exe and co_data:
            co_params.data = co_data
            area_CO, area_H_CO = CO.run(**co_params)
            self.electrode.area.H = area_H_CO
            self.electrode.area.CO = area_CO
            self.electrode.catalyst.set_ecsa(area_CO)


        # ORR
        orr_params = self.analysis_params.orr

        orr_data = dict()
        for name, filename in orr_params.data.items():
            i_data = self.data.get(filename)
            if i_data:
                orr_data[name] = i_data
        if orr_params.exe and orr_data:
            orr_params.catalyst_mass = self.electrode.catalyst.active_center.mass
            orr_params.area_geometric = self.electrode.area.geom
            orr_params.area_real = self.electrode.area.big()
            if self.electrode.area.CO:
                orr_params.area_real = self.electrode.area.CO
            del orr_params['data']
            orr_params.orr_data = orr_data
            activities = ORR.run(**orr_params)
            self.orr_results = activities

    def __str__(self):
        text = (f'{self.electrode}'
                f'{self.orr_results}')

        return text
# ..
