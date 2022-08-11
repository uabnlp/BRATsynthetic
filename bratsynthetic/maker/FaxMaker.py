from .PhoneMaker import PhoneMaker


class FaxMaker(PhoneMaker):

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'

        output = self.make_phone_number()

        if output.upper() == 'UNMATCHED':
            output = self.make_phone_number()

        return output
