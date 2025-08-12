from .Maker import Maker
import logging

logger = logging.getLogger('BratSynthetic')

class BioIDMaker(Maker):

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'
        output = self.make_matching_alphanumeric(input)

        if self.config.general.show_replacements:
            logger.info(f'    BioIDMaker: {input} -> {output}')

        if output.upper() == 'UNMATCHED':
            output = self.make_matching_alphanumeric(input)

        return output
