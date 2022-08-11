from .Maker import Maker


class StateMaker(Maker):

    def make_one(self, input: str) -> str:
        output = self.fake.state_abbr(False) if len(input) < 3 else self.fake.state()
        output = self.match_case(input, output)

        return output
