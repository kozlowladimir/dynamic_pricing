import numpy as np

from default_strategy import default_strategy


def ceil_to_base(x, base=2):
    if x == 0:
        return base
    return int(base * np.ceil(x / base))


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
