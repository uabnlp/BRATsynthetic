# PatientMaker.py

from .NameMakerBase import NameMaker

class PatientMaker(NameMaker):
    def __init__(self, config):
        # Use seed_offset = 2 for PatientMaker
        super().__init__(config, seed_offset=2)
