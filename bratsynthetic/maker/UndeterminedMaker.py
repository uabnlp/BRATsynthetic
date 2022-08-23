import random
import re
import string

from .Maker import Maker


class UndeterminedMaker(Maker):

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'


        if re.fullmatch(r'[a-z]+', input, re.IGNORECASE) and len(input) < 5:
            output = ''
            for i in range(len(input)):
                output = output + random.choice(string.ascii_letters)

        output = self.match_case(input, output)

        if self.config.general.show_replacements:
            print(f'    UndeterminedMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.make_matching_alphanumeric(input)


        return output
