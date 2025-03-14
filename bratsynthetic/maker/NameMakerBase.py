import re
from typing import List, Dict
import logging
from bratsynthetic.maker import Maker

logger = logging.getLogger('BratSynthetic')

class NameMaker(Maker):
    def __init__(self, config, seed_offset: int = 0):
        super().__init__(config, seed_offset)
        # Initialize replacement dictionaries for each instance
        self.first_name_replacements: Dict[str, str] = {}
        self.last_name_replacements: Dict[str, str] = {}

    def make_random(self, input_list: List[str]) -> List[str]:
        return self.make_markov(input_list, 1.0)

    def make_consistent_name(self, input_list: List[str]) -> List[str]:
        return self.make_markov(input_list, 0.0)

    def make_markov(self, input_list: List[str], transition_probability: float = 0.5) -> List[str]:
        ret_list: List[str] = []

        for original_input in input_list:
            if transition_probability == 1.0:
                do_transition = True
            elif transition_probability == 0.0:
                do_transition = False
            else:
                do_transition = self.random.uniform(0, 1) >= transition_probability

            input_str = original_input.strip()
            words = re.split(r'[,\s]+', input_str)
            first_name = None
            last_name = None

            if len(words) == 0:
                pass
            elif len(words) == 1:
                # Assume last name only
                last_name = words[0]
            elif ',' in original_input:
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
                key_last_name = last_name.lower()
                if key_last_name in self.last_name_replacements and not do_transition:
                    replacement_last_name = self.last_name_replacements[key_last_name]
                else:
                    replacement_last_name = self.fake.last_name()
                    self.last_name_replacements[key_last_name] = replacement_last_name

            if first_name is not None:
                key_first_name = first_name.lower()
                if key_first_name in self.first_name_replacements and not do_transition:
                    replacement_first_name = self.first_name_replacements[key_first_name]
                else:
                    replacement_first_name = self.fake.first_name()
                    self.first_name_replacements[key_first_name] = replacement_first_name

            replacement_name = "UNMATCHED"
            if replacement_first_name is not None and replacement_last_name is not None:
                if ',' in original_input:
                    replacement_name = f"{replacement_last_name}, {replacement_first_name}"
                else:
                    replacement_name = f"{replacement_first_name} {replacement_last_name}"
            elif replacement_last_name is not None:
                replacement_name = replacement_last_name
            elif replacement_first_name is not None:
                replacement_name = replacement_first_name

            output = self.match_case(original_input, replacement_name)

            if self.config.general.show_replacements:
                logger.info(f"{self.__class__.__name__} - : {original_input} -> {output}")

            if output.upper() == 'UNMATCHED':
                output = self.match_case(original_input, self.fake.name())

            ret_list.append(output)

        return ret_list
