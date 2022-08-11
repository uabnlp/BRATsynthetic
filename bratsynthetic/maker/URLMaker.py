from .Maker import Maker

class URLMaker(Maker):

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'

        output = self.fake.url()

        if self.show_replacements:
            print(f'    URLMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.fake.url()

        return output
