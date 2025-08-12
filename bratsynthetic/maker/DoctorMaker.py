# DoctorMaker.py

from .NameMakerBase import NameMaker

class DoctorMaker(NameMaker):
    def __init__(self, config):
        # Use seed_offset = 1 for DoctorMaker
        super().__init__(config, seed_offset=1)
