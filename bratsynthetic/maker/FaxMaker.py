from .PhoneMaker import PhoneMaker


class FaxMaker(PhoneMaker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        output = self.make_phone_number()

        if self.show_replacements:
            print(f'    FaxMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.make_phone_number()

        return output
