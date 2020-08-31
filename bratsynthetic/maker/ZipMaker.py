from .Maker import Maker

class ZipMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        output = self.fake.postcode()

        print(f'ZipMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.fake.postcode()

        return output
