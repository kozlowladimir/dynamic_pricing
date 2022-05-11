from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from default_strategy import default_strategy


def ceil_to_base(x, base=2):
    if x == 0:
        return base
    return int(base * np.ceil(x / base))


class AbstractPricingSomeMethod(ABC):
    """
    Абстрактый класс для реализации различных стратегий ценообразования
    """

    def __init__(self, nominal_price, threshold, explore_count=500):
        self.BAR = nominal_price
        self.RackRate = 1.5 * nominal_price
        self.Netto = 0.5 * nominal_price
        self.history = pd.DataFrame(columns=['price', 'acceptance'])
        self.price_steps_count = 40
        self.price_step = (self.RackRate - self.Netto) / self.price_steps_count
        self.prices = [self.Netto + x * self.price_step for x in range(self.price_steps_count + 1)]
        self.average_period = 7
        self.event_queue = {x: [0] for x in range(31)}
        self.threshold = threshold
        self.explore_count = explore_count

    def update_history(self, event):
        self.history = pd.concat([self.history, pd.DataFrame(event, index=[0])])

    def update_queue(self, events_dict):
        for key in events_dict:
            if len(self.event_queue[key]) == 7:
                self.event_queue[key].pop(0)
            self.event_queue[key].append(events_dict[key])

    def get_average_orders(self, depth):
        result = 0
        for x in range(depth + 1):
            result += sum(self.event_queue[x])
        return result

    @abstractmethod
    def set_price(self, hotel, request, verbose=0):
        pass


class PricingDefault:
    """
    Дефолтная стратегия ценообразования
    """
    def __init__(self, nominal_price):
        self.BAR = nominal_price
        self.RackRate = 1.5 * nominal_price
        self.Netto = 0.5 * nominal_price

    def set_price(self, hotel, request):
        load = hotel.get_loading(request.start_day) / hotel.number_of_rooms * 100
        load = ceil_to_base(load)

        depth = request.depth
        depth = ceil_to_base(depth)
        value = default_strategy[(load, depth)] / 100

        return self.RackRate - (self.RackRate - self.Netto) * value


class PricingConstant:
    """
    Константная цена
    """
    def __init__(self, price):
        self.price = price

    def set_price(self, hotel, request):
        return self.price


class PricingRandom:
    """
    Константная цена
    """
    def __init__(self, nominal_price):
        self.BAR = nominal_price
        self.RackRate = 1.5 * nominal_price
        self.Netto = 0.5 * nominal_price
        self.step = 40
        self.price_step = self.BAR/self.step

    def set_price(self, hotel, request):
        rand_int = np.random.randint(self.step + 1)

        return self.Netto + rand_int * self.price_step


class PricingSomeMethod(AbstractPricingSomeMethod):
    """
    Класс, описывающий одну из стратегий ценообразования
    """

    def calc_price(self, rs: pd.DataFrame) -> int:
        if not len(rs[rs > self.threshold]):
            return rs.index[-1]
        else:
            return rs[rs > self.threshold].index[0]

    def set_price(self, hotel, request, verbose=0):

        if len(self.history) > self.explore_count + len(self.prices):
            rest = self.get_average_orders(request.depth) / (
                        hotel.number_of_rooms - hotel.get_loading(request.start_day))

            p = self.history.groupby('price')['acceptance'].mean()
            count = self.history.groupby('price')['acceptance'].count()
            rs = ((p + (p * (1 - p) / count) ** 0.5) * rest).sort_values()
            if verbose:
                print(p)
                print(f'rest: {rest}')
                print(rs)

            price = self.calc_price(rs)
        else:
            price = self.prices[np.random.randint(len(self.prices))]
        return price
