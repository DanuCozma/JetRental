# models/factories.py
from abc import abstractmethod, ABC

from db_models import Jets


class Factory(ABC):
    @abstractmethod
    def create(self, name, model, year, color, price, image_url):
        pass


class JetFactory(Factory):
    def create(self, name, model, year, engine, color,  price, image_url):
        if not all([name, model, year, color, engine, price, image_url]):
            raise ValueError("Incomplete jet information. Make sure all attributes are set.")

        # Create and return a new Jets object
        return Jets(
            name=name,
            model=model,
            year=year,
            color=color,
            engine=engine,
            price=price,
            image_url=image_url
        )


