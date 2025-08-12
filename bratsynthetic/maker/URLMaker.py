import logging
from .Maker import Maker

logger = logging.getLogger('BratSynthetic')

class URLMaker(Maker):

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'
        
        output = self.fake.url()
        
        if self.config.general.show_replacements:
            logger.info(f'    URLMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.fake.url()
        
        return output
