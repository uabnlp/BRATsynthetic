import random

from .Maker import Maker


class HealthPlanMaker(Maker):

    _insurance = ['state insurance', 'Kaiser', 'medicare', 'medicaid', 'anthem', 'united', 'aetna']

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'

        output = random.choice(self._insurance)

        if self.config.general.show_replacements:
            print(f'    HealthPlanMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = random.choice(self._insurance)

        output = self.match_case(input, output)

        return output
