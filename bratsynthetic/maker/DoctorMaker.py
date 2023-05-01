from .NameMakerBase import NameMaker


class DoctorMaker(NameMaker):
    """
    Subclass of NameMaker because we want the PatientMaker and DoctorMaker to be separate classes.
    But right now they have exactly the same functionality.
    """
    pass
