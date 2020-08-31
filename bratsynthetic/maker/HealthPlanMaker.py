from .Maker import Maker

import random

class HealthPlanMaker(Maker):

    _insurance = ['state insurance', 'Kaiser', 'medicare', 'medicaid', 'anthem', 'united', 'aetna']

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        output = random.choice(self._insurance)

        # print(f'HealthPlanMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = random.choice(self._insurance)

        output = self.match_case(input, output)

        return output
