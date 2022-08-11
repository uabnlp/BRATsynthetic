import re

from .Maker import Maker


class DoctorMaker(Maker):

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'

        if re.fullmatch(r'\w+,.*', input):    # Assume [LAST], [FIRST]
            output = f'{self.fake.last_name()}, {self.fake.first_name()}'
        elif len(input.split(' ')) == 1:
            output = self.fake.last_name()
        else:
            output = self.fake.name()

        output = self.match_case(input, output)

        if output.upper() == 'UNMATCHED':
            output = self.fake.name()

        return output
