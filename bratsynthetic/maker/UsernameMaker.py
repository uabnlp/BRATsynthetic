from .Maker import Maker


class UsernameMaker(Maker):

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'

        #Guess email address
        if '@' and '.' in input:
            output = self.fake.ascii_email()
        else:
            output = self.fake.user_name()

        output = self.match_case(input, output)

        if output.upper() == 'UNMATCHED':
            output = self.match_case(self.fake.user_name())

        return output
