from abc import ABC, abstractmethod


class RentalStrategy(ABC):
    @abstractmethod
    def calculate_rental(self, rental_days, price_per_day):
        pass


class StandardPricingStrategy(RentalStrategy):
    def calculate_rental(self, rental_days, price_per_day):
        return rental_days * price_per_day


class MonthlyPricingStrategy(RentalStrategy):
    DISCOUNT_RATE = 0.8

    def calculate_rental(self, rental_days, price_per_day):
        total_price = rental_days * price_per_day
        return total_price * self.DISCOUNT_RATE
