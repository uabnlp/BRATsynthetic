from .Maker import Maker


class UsernameMaker(Maker):

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        #Guess email address
        if '@' and '.' in input:
            output = self.fake.ascii_email()
        else:
            output = self.fake.user_name()

        output = self.match_case(input, output)

        if self.show_replacements:
            print(f'UsernameMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.match_case(self.fake.user_name())

        return output
