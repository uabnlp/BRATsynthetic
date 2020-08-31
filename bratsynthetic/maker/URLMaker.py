from .Maker import Maker

class URLMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        output = self.fake.url()

        print(f'URLMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.fake.url()

        return output
