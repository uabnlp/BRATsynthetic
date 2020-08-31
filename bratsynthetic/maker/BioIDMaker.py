from .Maker import Maker


class BioIDMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        output = self.make_matching_alphanumeric(input)

        # print(f'BioIDMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.make_matching_alphanumeric(input)

        return output
