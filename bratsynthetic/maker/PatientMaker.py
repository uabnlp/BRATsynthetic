from .Maker import Maker


class PatientMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        words = input.split(' ')

        if len(words) == 1:
            output = self.fake.last_name()
        else:
            output = self.fake.name()

        output = self.match_case(input, output)
        # print(f'PatientMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.fake.name()

        return output
