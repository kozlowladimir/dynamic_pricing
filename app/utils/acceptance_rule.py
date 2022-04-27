from scipy.stats import bernoulli, norm


class AcceptanceRule:
    """
    Эластичность спроса по цене: при цене, равной номинальной, вероятность принятия запроса 0.5.
    При другой цене вероятность принятия 1 - Phi(rho (price_{algo} - price_{nominal})),
    где Phi -- cdf стандартного нормального распределения, а rho таким образом, что вероятность принятия при
    отклонении на 50% от номинальной цены 0 и 1 соответственно.
    Здесь price_{algo} и price_{nominal} нормированы относительно price_{nominal}, т.е. price_{nominal} = 1.
    """
    def __init__(self, nominal_price=None, rho=None):
        """
        Инициализация
        :param nominal_price: номинальная цена
        :param rho: параметр rho
        """
        if not nominal_price:
            self.nominal_price = 1000
        else:
            self.nominal_price = nominal_price

        if not rho:
            self.rho = 4.66

    def decision(self, price):
        """
        Принятие решения о бронировании при указанной цене
        :param price: цена
        :return: забронировали или нет
        """
        acceptance_chance = 1 - norm.cdf(self.rho * (price / self.nominal_price - 1))
        return bernoulli(acceptance_chance).rvs()
