from abc import abstractmethod, ABC

from models import Jet


class JetDecorator(Jet, ABC):
    def __init__(self, jet):
        self.jet = jet

    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def price(self):
        pass


class MaxSpeed(JetDecorator):
    def __init__(self, jet):
        super().__init__(jet)

    def description(self):
        return f"{super().description()}, Max Speed: km/h"

    def price(self):
        return self.jet.price() + 15


class GPS(JetDecorator):
    def __init__(self, jet):
        super().__init__(jet)

    def description(self):
        return f"{super().description()}, GPS: Yes"

    def price(self):
        return self.jet.price() + 20

class RoofBag(JetDecorator):
    def __init__(self, jet):
        super().__init__(jet)

    def description(self):
        return f"{super().description()}, Roof Bag: Yes"

    def price(self):
        return self.jet.price() + 30
