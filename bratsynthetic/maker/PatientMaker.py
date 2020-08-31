from .Maker import Maker

import re

class PatientMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        words = input.split(' ')

        if re.fullmatch(r'\w+,.*', input):    # Assume [LAST], [FIRST]
            output = f'{self.fake.last_name()}, {self.fake.first_name()}'
        elif len(words) == 1:
            output = self.fake.last_name()
        else:
            output = self.fake.name()

        output = self.match_case(input, output)
        if self.show_replacements:
            print(f'    PatientMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.fake.name()

        return output
