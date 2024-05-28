# models/jet.py
import copy


class Jet:
    def __init__(self):
        self.name = None
        self.model = None
        self.year = None
        self.color = None
        self.price = None
        self.image_url = None

    def clone(self):
        return copy.deepcopy(self)

    # def description(self):
    #    return f"{self.name} {self.model} {self.year} ({self.color})"
