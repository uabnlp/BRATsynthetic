from .Maker import Maker


class OrganizationMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        if len(input) < 5:
            output = ''.join([letter for letter in self.fake.company() if letter.isupper()])
        else:
            output = self.fake.company()

        output = self.match_case(input, output)

        if self.show_replacements:
            print(f'    OrganizationMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.match_case(self.fake.company())

        return output
