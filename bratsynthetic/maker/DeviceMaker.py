from .Maker import Maker


class DeviceMaker(Maker):

    def make_one(self, input: str) -> str:
        output = self.make_matching_alphanumeric(input)
        return output
