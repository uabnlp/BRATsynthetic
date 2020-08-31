
from .Maker import Maker

import re

class StreetMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        # Numbered Street Address
        if re.match(r'\d+', input) != None:
            output = self.fake.street_address()
        # Just the street name
        else:
            output = self.fake.street_name()

        output = self.match_case(input, output)
        print(f"StreetMaker: {input} -> {output}")
        if output == 'UNMATCHED':
            output = self.fake.street_address()

        return output

