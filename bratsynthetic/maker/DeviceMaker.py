from .Maker import Maker


class DeviceMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        output = self.make_matching_alphanumeric(input)

        if self.show_replacements:
            print(f'DeviceMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.make_matching_alphanumeric(input)

        return output
