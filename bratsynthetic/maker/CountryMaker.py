from .Maker import Maker


class CountryMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        if len(input) < 4:
            output = self.fake.country_code()
        else:
            output = self.fake.country()

        output = self.match_case(input, output)

        if self.show_replacements:
            print(f'CountryMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.match_case(input, self.fake.country())

        return output
