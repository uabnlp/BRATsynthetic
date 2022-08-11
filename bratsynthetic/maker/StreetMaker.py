
import re

from .Maker import Maker


class StreetMaker(Maker):

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'

        # Numbered Street Address
        if re.match(r'\d+', input) != None:
            output = self.fake.street_address()
        # Just the street name
        else:
            output = self.fake.street_name()

        output = self.match_case(input, output)

        if output == 'UNMATCHED':
            output = self.fake.street_address()

        return output

