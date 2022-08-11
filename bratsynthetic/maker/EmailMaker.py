from .Maker import Maker


class EmailMaker(Maker):

    def make_one(self, input: str) -> str:
        output = self.fake.ascii_free_email()
        return output
