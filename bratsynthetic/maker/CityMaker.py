from .Maker import Maker


class CityMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        output = self.fake.city()

        output = self.match_case(input, output)

        # print(f'CityMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.match_case(input, self.fake.city())

        return output
