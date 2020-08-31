from .Maker import Maker

import re
import random

class TimeMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        add_colon = ':' in input
        add_meridian = (re.search(r'[ap]\.?m', input, re.IGNORECASE)) != None
        with_periods = (re.search(r'[ap]\.'), input, re.IGNORECASE) != None
        #
        # if re.fullmatch(r'\d{2}:\d{2}', input):
        #     output = self.fake.time('%H:%M')
        # elif re.fullmatch(r'\d{2}'):
        #     output = self.fake.time('%H')
        # elif re.fullmatch(r'\d{4}'):
        #     output = self.fake.time('%H%M')
        # elif re.fullmatch(r'\d\d?([pa]\.?m\.?)'):
        #

        if add_colon and add_meridian:
            if with_periods:
                output = self.fake.time('%I:%M') + ' ' + random.choice(['A.M.', 'P.M.'])
            else:
                output = self.fake.time('%I:%M') + ' ' + random.choice(['AM', 'PM'])
        elif add_colon:
            output = self.fake.time('%H:%M')
        elif add_meridian:
            if with_periods:
                output = self.fake.time('%I%M') + ' ' + random.choice(['A.M.', 'P.M.'])
            else:
                output = self.fake.time('%I%M') + ' ' + random.choice(['AM', 'PM'])
        else:
            output = self.fake.time('%H%M')

        output = self.match_case(input, output)

        print(f'TimeMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.fake.time('%H%M')

        return output
