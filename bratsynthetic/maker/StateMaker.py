from .Maker import Maker


class StateMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        if len(input) < 3:
            output = self.fake.state_abbr(False)
        else:
            output = self.fake.state()

        output = self.match_case(input, output)
        # print(f'StateMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.fake.state()

        return output
