from .Maker import Maker

import re
import random

class AgeMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        while True:
            match = re.fullmatch(r'(\d+)(\s*)(yo|y/o|mo|m/o|months|years|months old|years old|YO|Y/O|MO|M/O|Months|Years|Years Old|Months Old)?', input)
            if match:
                age, space, unit = match.groups()
                age_int = int(age)

                age = str(max(random.randint(age_int - 5, age_int + 5), 1))
                if not unit:
                    unit = ""
                output = age + space + unit
                break


            match = re.fullmatch(r'(\d+)-(\d+)(\s*)(yo|y/o|mo|m/o|months|years|months old|years old|YO|Y/O|MO|M/O|Months|Years|Years Old|Months Old)?', input)
            if match:
                age1, age2, space, unit = match.groups()
                offset = random.randint(-5, +5)

                age1_int, age2_int = max(1, int(age1) + offset), max(1, int(age2) + offset)
                if not unit:
                    unit = ""

                output = str(age1_int) + '-' + str(age2_int) + space + unit
                break

            break

        output = self.match_case(input, output)
        if self.show_replacements:
            print(f'AgeMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = str(random.randint(18, 79))

        return output
