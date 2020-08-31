from .Maker import Maker


class DoctorMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        if len(input.split(' ')) == 1:
            output = self.fake.last_name()
        else:
            output = self.fake.name()

        output = self.match_case(input, output)
        if self.show_replacements:
            print(f'    DoctorMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.fake.name()

        return output
