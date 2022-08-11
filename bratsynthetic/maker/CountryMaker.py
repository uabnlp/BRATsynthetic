from .Maker import Maker


class CountryMaker(Maker):

    def make_one(self, input: str) -> str:

        output = self.fake.country_code() if len(input) < 4 else self.fake.country()
        output = self.match_case(input, output)

        return output
