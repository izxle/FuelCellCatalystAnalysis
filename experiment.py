from electrode import Electrode
from reader import Data


class Experiment:
    def __init__(self, data: Data, electrode: Electrode):
        self.data = data
        self.electrode = electrode

    def analyze(self):
        pass
# ..
