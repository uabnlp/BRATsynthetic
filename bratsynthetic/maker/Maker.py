import random
import re
from typing import List, Dict
import logging
from faker import Faker

from bratsynthetic import BratSyntheticConfig

logger = logging.getLogger('BratSynthetic')

class Maker:
    def __init__(self, config: BratSyntheticConfig, seed_offset: int = 0):
        SEED = config.general.seed + seed_offset
        self.fake: Faker = Faker()
        self.fake.seed_instance(SEED)
        self.random = random.Random(SEED)
        self.config: BratSyntheticConfig = config

    """
    Template method. Subclasses should fill this in.
    """
    def make_one(self, input: str) -> str:
        output: str = 'UNMATCHED'
        if self.config.general.show_replacements:
            logger.info(f"{self.__class__.__name__} - : {input} -> {output}")
        return output

    def make(self, input_list: List[str]) -> List[str]:
        strat_func = self.get_strategy()
        output_list = strat_func(input_list)
        return output_list

    def get_transition_probability(self):
        return self.config.general.default_transition_probability

    def get_strategy(self):
        strat: str = self.config.general.default_strategy

        if strat == 'markov':
            transition_probability: float = self.get_transition_probability()
            strat_func = lambda input_list: self.make_markov(input_list, transition_probability)
        elif strat == 'consistent':
            strat_func = lambda input_list: self.make_markov(input_list, 0.0)
        elif strat == 'random':
            strat_func = lambda input_list: self.make_markov(input_list, 1.0)
        else:
            raise ValueError(f"Unknown strategy: {strat}")

        return strat_func

    def make_markov(self, input_list: List[str], transition_probability: float = 0.5):
        ret_list: List[str] = []
        replacements: Dict[str, str] = {}

        for original_input in input_list:
            if transition_probability == 1.0:
                do_transition = True
            elif transition_probability == 0.0:
                do_transition = False
            else:
                do_transition = self.random.uniform(0, 1) < transition_probability

            # use uppercase version as key for consistency
            input_key = original_input.strip().upper()
            if input_key in replacements and not do_transition:
                replacement = self.match_case(original_input, replacements[input_key])
            else:
                replacement = self.make_one(original_input)
                replacements[input_key] = replacement

            output = replacement

            if self.config.general.show_replacements:
                logger.info(f"    {self.__class__.__name__} - : {original_input} -> {output}")

            ret_list.append(output)

        return ret_list

    def make_matching_alphanumeric(self, template: str) -> str:
        """
        Creates a new string with random letters and numbers replacing the originals.
        Example - Template: A534 AKQ-938 -> "P284 PJE-736"
        """
        upper_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        lower_letters = 'abcdefghijklmnopqrstuvwxyz'
        numbers = '0123456789'

        output = ''
        for character in template:
            if character in upper_letters:
                output += self.random.choice(upper_letters)
            elif character in lower_letters:
                output += self.random.choice(lower_letters)
            elif character in numbers:
                output += self.random.choice(numbers)
            else:
                output += character

        return output

    def match_case(self, template: str, string: str) -> str:
        """
        Attempts to match the case of the template.
        """
        if template.istitle():
            return string.title()
        elif template.islower():
            return string.lower()
        elif template.isupper():
            return string.upper()
        if re.search('[a-zA-Z]', template):
            logger.warning(f"    Unhandled match_case: {template}")
        return string
