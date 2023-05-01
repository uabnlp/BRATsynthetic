import random
import re
import sys
from typing import List, Dict

from faker import Faker

from bratsynthetic.maker import Maker

SEED = random.randint(~sys.maxsize, sys.maxsize)
Faker.seed(SEED)
random.seed = SEED

class NameMaker(Maker):

    def make_random(self, input_list: List[str]) -> List[str]:
        return self.make_markov(input_list, 1.0)

    def make_consistent_name(self, input_list: List[str]) -> List[str]:
        return self.make_markov(self, input_list, -1.0)

    def make_markov(self, input_list: List[str], transition_probability: float = 0.5) -> List[str]:
        ret_list: List[str] = []

        first_name_replacements: Dict[str, str] = {}
        last_name_replacements: Dict[str, str] = {}

        for original_input in input_list:
            if transition_probability == 1.0:
                do_transistion = True
            elif transition_probability == 0.0:
                do_transistion = False
            else:
                do_transistion = random.uniform(0, 1) >= transition_probability

            input = original_input.strip().upper()
            words = re.split(r'[,\s]+', input)
            first_name = None
            last_name = None
            if len(words) == 0:
                pass
            elif len(words) == 1:
                # Assume last name only
                last_name = words[0]
            elif ',' in input:
                # Assume LASTNAME, FIRSTNAME
                last_name = words[0]
                first_name = words[1]
            else:
                # Assume FIRSTNAME LASTNAME
                first_name = words[0]
                last_name = words[1]

            replacement_first_name = None
            replacement_last_name = None
            if last_name is not None:
                if last_name in last_name_replacements.keys() and not do_transistion:
                    replacement_last_name = last_name_replacements[last_name]
                else:
                    replacement_last_name = self.fake.last_name()
                    last_name_replacements[last_name] = replacement_last_name

            if first_name is not None:
                if first_name in first_name_replacements.keys() and not do_transistion:
                    replacement_first_name = first_name_replacements[first_name]
                else:
                    replacement_first_name = self.fake.first_name()
                    first_name_replacements[first_name] = replacement_first_name


            replacement_name = "UNMATCHED"
            if replacement_first_name is not None and replacement_last_name is not None:
                if ',' in input:
                    replacement_name = f"{replacement_last_name}, {replacement_first_name}"
                else:
                    replacement_name = f"{replacement_first_name} {replacement_last_name}"
            elif replacement_last_name is not None:
                replacement_name = replacement_last_name
            elif replacement_first_name is not None:
                replacement_name = replacement_first_name

            output = self.match_case(input, replacement_name)
            if self.config.general.show_replacements:
                print(f"{self.__class__.__name__} - : {input} -> {output}")
            if output.upper() == 'UNMATCHED':
                output = self.match_case(self.fake.name())

            ret_list.append(output)

        return ret_list


