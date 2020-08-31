
from faker import Faker
import random
import sys

SEED = random.randint(~sys.maxsize, sys.maxsize)
Faker.seed(SEED)
random.seed = SEED

class Maker:

    def __init__(self):
        self.fake = Faker()

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
            string.capitalize()
        elif template.islower():
            return string.lower()
        elif template.isupper():
            return string.upper()
        # ELSE
        # print(f"Unhandled match_case: {template}")

        return string
