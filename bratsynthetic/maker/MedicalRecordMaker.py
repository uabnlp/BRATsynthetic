from .Maker import Maker

class MedicalRecordMaker(Maker):

    def make_one(self, input: str) -> str:
        output = self.make_matching_alphanumeric(input)
        return output
