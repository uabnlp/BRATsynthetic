from .Maker import Maker


class CityMaker(Maker):

    def make_one(self, input: str) -> str:

        output = self.match_case(input, self.fake.city())
        return output
