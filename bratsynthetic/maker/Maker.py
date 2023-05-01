import random
import re
from typing import List, Dict

from faker import Faker

from bratsynthetic import BratSyntheticConfig


class Maker:

    def __init__(self, config: BratSyntheticConfig):
        SEED = config.general.seed
        Faker.seed(SEED)
        random.seed = SEED
        self.fake: Faker = Faker()
        self.config: BratSyntheticConfig = config


    """
    Template method. Subclasses should fill this in.
    """
    def make_one(self, input: str) -> str:
        output: str = 'UNMATCHED'
        if self.config.general.show_replacements:
            print(f"{self.__class__.__name__} - : {input} -> {output}")
        return output

    def make(self, input_list: List[str]) -> List[str]:
        strat_func = self.get_strategy()

        output_list = strat_func(input_list)
        return output_list

    def get_transition_probability(self):
        return self.config.general.default_transition_probability

    def get_strategy(self) -> str :
        strat: str = self.config.general.default_strategy

        if strat == 'markov':
            transition_probability:float = self.get_transition_probability()
            strat_func = lambda input_list: self.make_markov(input_list, transition_probability)
        if strat == 'consistent':
            strat_func = lambda input_list: self.make_markov(input_list, 0.0)
        if strat == 'random':
            strat_func = lambda input_list: self.make_markov(input_list, 1.0)

        return strat_func

    def make_markov(self, input_list:List[str], transition_probability: float = 0.5):
        ret_list: List[str] = []

        replacements: Dict[str, str] = {}

        for original_input in input_list:
            if transition_probability == 1.0:
                do_transistion = True
            elif transition_probability == 0.0:
                do_transistion = False
            else:
                do_transistion = random.uniform(0, 1) >= transition_probability

            input = original_input.strip().upper()
            replacement = None
            if input in replacements and not do_transistion:
                replacement = self.match_case(original_input, replacements[input])
            else:
                replacement = self.make_one(original_input)
                replacements[input] = replacement

            output = replacement

            if self.config.general.show_replacements:
                print(f"    {self.__class__.__name__} - : {original_input} -> {output}")

            ret_list.append(output)

        return ret_list


    def make_matching_alphanumeric(self, template: str) -> str:
        """
        Creates a new string with random letters and number replacing the originals.
        Example - Template: A534 AKQ-938 -> "P284 PJE-736"

        :param template: String that determine the location of random letters and numbers
        :return: String randomizing the letters and a numbers in the template string
        """

        upper_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        lower_letters = 'abcdefghijklmnopqrstuvwxyz'
        numbers = '0123456789'

        output = template
        for replacements in [upper_letters, lower_letters, numbers]:
            for character in replacements:
                output = output.replace(character, random.choice(replacements))

        return output


    def match_case(self, template: str, string: str) -> str:
        """
        Attempts to match the case of the template. Return new string based on template casing
        Checks for title, lower, and upper case.

        Examples:
            * match_case('NOV', 'dec') -> 'DEC'
            * match_case('Hello World!', 'GREAT NEWS!') -> 'Great News!'
            * match_case('frodo was here', 'Hello') -> 'hello'

        :param template: string to match case to
        :param string: string to alter case to match input
        :return: altered string matching the case of the original string
        """

        if template.istitle():
            return string.title()
        elif template.islower():
            return string.lower()
        elif template.isupper():
            return string.upper()
        # ELSE
        if re.search('[a-zA-Z]', template):
            print(f"    Unhandled match_case: {template}")
        return string
