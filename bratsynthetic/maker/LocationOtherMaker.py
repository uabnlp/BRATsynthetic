from .Maker import Maker

import random

_locations = ['McDonalds', 'Waffle House', 'TacoBell', 'Movie Theater', 'fast food restaurant', 'diner',
'grocery store', 'park', 'library', 'school']

class LocationOtherMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        output = random.choice(_locations)

        output = self.match_case(input, output)

        # print(f'LocationOtherMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.match_case(random.choice(_locations))

        return output
