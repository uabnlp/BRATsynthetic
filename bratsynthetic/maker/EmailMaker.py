from .Maker import Maker


class EmailMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        output = self.fake.ascii_free_email()

        if self.show_replacements:
            print(f'EmailMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.fake.ascii_free_email()

        return output
