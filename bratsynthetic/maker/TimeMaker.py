import random
import re

from .Maker import Maker


class TimeMaker(Maker):

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'

        add_colon = ':' in input
        add_meridian = (re.search(r'[ap]\.?m', input, re.IGNORECASE)) != None
        with_periods = (re.search(r'[ap]\.', input, re.IGNORECASE)) != None

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

        if output.upper() == 'UNMATCHED':
            output = self.fake.time('%H%M')

        return output
