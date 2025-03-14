import random
import re
import string
import logging

from .Maker import Maker

logger = logging.getLogger('BratSynthetic')

class UndeterminedMaker(Maker):

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'

        # If input is all alphabetic and shorter than 5 characters,
        # generate a new string with random letters of the same length.
        if re.fullmatch(r'[a-z]+', input, re.IGNORECASE) and len(input) < 5:
            output = ''
            for i in range(len(input)):
                output += random.choice(string.ascii_letters)

        output = self.match_case(input, output)

        if self.config.general.show_replacements:
            logger.info(f'    UndeterminedMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.make_matching_alphanumeric(input)

        return output
