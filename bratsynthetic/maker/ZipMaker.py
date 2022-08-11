from .Maker import Maker

class ZipMaker(Maker):

    def make_one(self, input: str) -> str:
        output = self.fake.postcode()
        return output
