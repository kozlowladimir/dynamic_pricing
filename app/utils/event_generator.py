import sys
sys.path.append('D:/git/dynamic_pricing/app/utils')

import numpy as np
from scipy.stats import bernoulli, poisson, rv_discrete

from request import Request


class EventGenerator:
    """
    Класс, отвечающий за генерацию запросов.
    Многие цифры в распределениии являются "магическими"
    и были выявлены опытным путем куратором проекта.
    """
    def __init__(
            self,
            rv_LoS=None,
            rv_persons=None,
            rv_depth=None,
            rv_request_number=None,
            rv_cancelation=None,
            mu=None
    ):
        """
        Инициализация
        :param rv_LoS: распределение продолжительности заказа
        :param rv_persons: распределение числа гостей
        :param rv_depth: распределение глубины бронирования
        :param rv_request_number: распределение числа запросов
        :param rv_cancellation: распределение отмены броней
        :param mu: интенсивность прибытия
        """

        if not rv_LoS:
            x_LoS = np.arange(1, 9)
            y_LoS = [0.382844, 0.217141, 0.153037, 0.100752, 0.059283, 0.038609, 0.033461, 0.014873]
            self.rv_LoS = rv_discrete(name='LoS', values=(x_LoS, y_LoS))
        else:
            self.rv_LoS = rv_LoS

        if not rv_persons:
            x_persons = np.arange(1, 6)
            y_persons = [0.607341, 0.326343, 0.053066, 0.011490, 0.001760]
            self.rv_persons = rv_discrete(name='persons', values=(x_persons, y_persons))
        else:
            self.rv_persons = rv_persons

        if not rv_depth:
            x_depth = np.arange(31)
            y_depth = [0.215860, 0.119922, 0.081003, 0.063378, 0.049164, 0.040811, 0.035930,
                       0.030865, 0.028687, 0.027782, 0.023071, 0.021199, 0.020164, 0.018959,
                       0.019762, 0.017536, 0.017516, 0.016372, 0.015004, 0.013438, 0.014983,
                       0.012648, 0.012206, 0.012499, 0.011484, 0.010770, 0.010136, 0.010729,
                       0.009490, 0.009517, 0.009115]
            self.rv_depth = rv_discrete(name='depth', values=(x_depth, y_depth))
        else:
            self.rv_depth = rv_depth

        if not rv_request_number:
            self.rv_request_number = poisson(mu)

        if not rv_cancelation:
            chance = 0.25
            self.rv_cancellation = bernoulli(chance)

        self.rv_cancellation_depth = {}
        for depth in range(1, 31):
          i = np.arange(depth + 1)
          alpha = np.log(0.6) / np.log(depth / (depth + 1))
          y = ((depth + 1 - i) / (depth + 1)) ** alpha - ((depth - i) / (depth + 1)) ** alpha
          self.rv_cancellation_depth[depth] = rv_discrete(name='cancel', values=(i, y))

    def generate_cancellation(self, depth):
        """
        Генерация отмен брони. Фиксируем 40% отмен в последний день с распределением отмен
        ((R + 1 - i) / (R + 1)) ** alpha - ((R - i) / (R + 1)) ** alpha. тогда alpha = np.log(0.6) / np.log(R / (R + 1))
        :param depth: глубина заказа
        :return: глубина отмены
        """
        if self.rv_cancellation.rvs():
            if depth == 0:
                return None

            return self.rv_cancellation_depth[depth].rvs()
        else:
            return None

    def generate_one_request(self):
        """
        Генерация запроса на бронирование в соответствии с распределениями
        :return: экземпляр класса Request
        """
        LoS = self.rv_LoS.rvs()
        persons = self.rv_persons.rvs()
        depth = self.rv_depth.rvs()
        cancellation = self.generate_cancellation(depth)
        return Request(LoS, persons, depth, cancellation)

    def generate_requests(self):
        """
        Генерация запросов на бронирование в соответствии с распределением
        :return:
        """
        number_of_requests = self.rv_request_number.rvs()
        requests = []
        for k in range(number_of_requests):
            requests.append(self.generate_one_request())
        return requests